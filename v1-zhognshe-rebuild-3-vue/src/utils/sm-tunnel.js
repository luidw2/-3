/**
 * src/utils/sm-tunnel.js —— 前端安全隧道（对应后端 app/utils/tunnel.py）
 * =============================================================================
 * 前端负责两件事：
 *   发请求：生成一次性会话密钥 → 用后端公钥 SM2 封信封 → 用会话密钥 SM4 加密业务 JSON
 *           → 打包成 {"env": "...", "data": "..."} 作为整个请求体
 *   收响应：把响应的信封解开拿到新会话密钥 → SM4 解密业务数据
 *
 * 三条必须和后端对齐的规则（写错了只会解出乱码，很难查）：
 *   1) SM2 用 cipherMode = 0（C1‖C2‖C3）。后端 SM2.py 走的是 gmssl 的默认顺序，
 *      而 sm-crypto 默认是 1（C1‖C3‖C2），两种顺序的密文长度完全一样、看不出问题。
 *   2) sm-crypto 的公钥必须带 04 前缀，但 doEncrypt 的输出不带 04；
 *      后端是按"04 开头"识别信封的 —— 所以这里手动补上（发送）/ 去掉（接收）。
 *   3) SM4 用 CBC + PKCS#7，密钥与 IV 都是 16 字节 hex。
 *      实测：sm-crypto 的 SM4 与后端 gmssl 结果逐字节相同 ——
 *        key = iv = 000102030405060708090a0b0c0d0e0f, 明文 "AAAAAAA"
 *        -> 38601c5b95f1c60be75f7e103a0e0a74
 *
 * 用法：由 src/request.js 的拦截器自动调用，业务代码不用管。
 * =============================================================================
 */
import smCrypto from 'sm-crypto'

// sm-crypto 是 CommonJS 包，用默认导入再解构，Vite 与 Node 下都能跑
const { sm2, sm4 } = smCrypto

// Vite 里是 import.meta.env；用 Node 直接跑这个文件做联调测试时它不存在，故兜底
const ENV = import.meta.env || {}

// =============================================================================
// 一、密钥与协议常量
// =============================================================================
/**
 * 后端公钥（对应 .env 里的 SM2_FLASK_PUBLIC_KEY）：前端用它封装会话密钥。
 * 公钥不是秘密，直接放在前端没问题。可用 .env.local 的 VITE_ 变量覆盖。
 */
const FLASK_PUBLIC_KEY =
  ENV.VITE_SM2_FLASK_PUBLIC_KEY ||
  '34917afcd83e883bd107a7322079a963b1f3575c2050ca52d53cba7f118200b609ded86e20d0432c7032def98f763b27a6fddae3765989ba3dae4350d24b74a8'

/**
 * 前端自己的私钥（对应 .env 里的 SM2_VUE_PRIVATE_KEY）：用来拆后端回包的信封。
 *
 * ⚠️ Demo 说明：把私钥放在浏览器里本身并不安全（用户能看到），这里只是为了让
 *   "响应也加密"这条链路能完整跑通。真实项目应由后端下发会话密钥，前端不持私钥。
 */
const VUE_PRIVATE_KEY =
  ENV.VITE_SM2_VUE_PRIVATE_KEY ||
  '839aaadf3c4db79ffba124dec71308a56bd0df187fabdeb2c551cf9bd2af3de0'

const SM2_CIPHER_MODE = 0 // 0 = C1‖C2‖C3，与后端 gmssl 默认一致
const FIELD_ENV = 'env' // 报文里放 SM2 信封的字段
const FIELD_DATA = 'data' // 报文里放 SM4 密文的字段

/**
 * sm-crypto 要求的公钥形态：必须带 04 前缀。
 * （传裸的 128 位 hex 会直接报 "Invalid public key"，实测过）
 * 注意别和我们自己补在密文上的那个 04 搞混 —— 那个 04 是后端识别信封的约定。
 */
const FLASK_PUBLIC_KEY_04 = FLASK_PUBLIC_KEY.startsWith('04')
  ? FLASK_PUBLIC_KEY
  : '04' + FLASK_PUBLIC_KEY

/**
 * 需要走隧道的接口（和后端接口上的 @tunnel_required 一一对应）。
 * 后端给别的接口也加上装饰器时，这里同步加一条即可。
 */
export const TUNNEL_URLS = ['/user/login']

// =============================================================================
// 二、编码小工具（hex / bytes / base64 互转）
// =============================================================================
const hexToBytes = (hex) => {
  const out = new Uint8Array(hex.length / 2)
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.substr(i * 2, 2), 16)
  return out
}

const bytesToHex = (bytes) => {
  let s = ''
  for (let i = 0; i < bytes.length; i++) s += bytes[i].toString(16).padStart(2, '0')
  return s
}

const bytesToBase64 = (bytes) => {
  let s = ''
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i])
  return btoa(s)
}

const base64ToBytes = (b64) => {
  const s = atob(b64)
  const out = new Uint8Array(s.length)
  for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i)
  return out
}

/** 生成 n 字节的随机十六进制串（会话密钥 / IV / nonce 都用它） */
const randomHex = (n) => bytesToHex(crypto.getRandomValues(new Uint8Array(n)))

// =============================================================================
// 三、对外两个函数
// =============================================================================
/**
 * 把业务数据封成隧道请求体（字符串形式的 JSON）。
 * 对应后端 tunnel.py 的 seal_request()。
 *
 * @param {object} payload 业务请求体，例如 { username, password, role }
 * @returns {string} '{"env":"...","data":"..."}'
 */
export function sealRequest(payload) {
  // 1) 生成一次性会话密钥 / IV / nonce / 时间戳
  const keyblob = {
    key: randomHex(16),
    iv: randomHex(16),
    nonce: randomHex(16),
    ts: Date.now() // 毫秒时间戳，后端校验 ±5 分钟
  }

  // 2) SM2 封装会话密钥。
  //    两处 04 含义不同：公钥带 04 是 sm-crypto 的格式要求；
  //    密文外面补 04 是后端识别信封的约定（sm-crypto 的输出不带 04）。
  const envelopeHex =
    '04' + sm2.doEncrypt(JSON.stringify(keyblob), FLASK_PUBLIC_KEY_04, SM2_CIPHER_MODE)

  // 3) SM4 加密业务 JSON（返回 hex）
  const dataHex = sm4.encrypt(JSON.stringify(payload), keyblob.key, {
    mode: 'cbc',
    iv: keyblob.iv
  })

  // 4) 打包：信封与密文都转成 base64（和后端的编码保持一致）
  //    注意 sm-crypto 的 sm4.encrypt 返回的是 hex，必须转成 base64 再放进去，
  //    否则后端拿 hex 当 base64 解，只会解出乱码。
  return JSON.stringify({
    [FIELD_ENV]: bytesToBase64(hexToBytes(envelopeHex)),
    [FIELD_DATA]: bytesToBase64(hexToBytes(dataHex))
  })
}

/**
 * 拆开隧道响应，返回业务数据（对象）。
 * 对应后端 tunnel.py 的 open_response()。
 *
 * 注意：隧道校验失败时后端会返回【明文 JSON】（那时没有可用的会话密钥），
 * 这种情况下报文里没有 env 字段，直接原样返回，交给业务/错误处理。
 *
 * @param {object|string} data 响应体（axios 已解析成对象，或原始字符串）
 * @returns {object} 业务数据
 */
export function openResponse(data) {
  let pack = data
  if (typeof pack === 'string') {
    try {
      pack = JSON.parse(pack)
    } catch (e) {
      return data
    }
  }
  if (!pack || typeof pack !== 'object' || !pack[FIELD_ENV]) {
    return pack // 明文响应（例如隧道错误码），原样返回
  }

  // 1) 信封：base64 -> hex，并去掉 04 前缀（sm-crypto 的 doDecrypt 要求不带 04）
  let envelopeHex = bytesToHex(base64ToBytes(pack[FIELD_ENV]))
  if (envelopeHex.startsWith('04')) envelopeHex = envelopeHex.slice(2)

  // 2) 拆信封拿到会话密钥
  const keyblob = JSON.parse(sm2.doDecrypt(envelopeHex, VUE_PRIVATE_KEY, SM2_CIPHER_MODE))

  // 3) SM4 解密业务数据（sm4.decrypt 要 hex，而线上是 base64，先转一下）
  const dataHex = bytesToHex(base64ToBytes(pack[FIELD_DATA]))
  const plain = sm4.decrypt(dataHex, keyblob.key, {
    mode: 'cbc',
    iv: keyblob.iv
  })
  return JSON.parse(plain)
}

/** 判断这个请求地址是否需要走隧道（供 request.js 的拦截器使用） */
export function isTunnelUrl(url = '') {
  // 去掉查询串再比对，避免 '/user/login?x=1' 匹配不上
  const path = url.split('?')[0]
  return TUNNEL_URLS.includes(path)
}
