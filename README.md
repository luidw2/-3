# -3

第五组学校综设项目：基于 Flask + Vue3 + SM2/SM3/SM4 国密算法的安全电子商务系统。

第 4 周节点：应用层安全隧道 Demo。敏感接口（当前为 `POST /user/login`）的请求/响应业务 JSON 在 Axios 拦截器中加密，传输层同时保持 HTTPS。

## 目录结构

```
-3/
├── 后端flask/                     # Flask 后端
│   ├── run.py                     # 启动入口（HTTPS 127.0.0.1:5000）
│   ├── requirements.txt           # Python 依赖清单
│   ├── .env.example                # 环境变量模板（复制为 .env 后填写）
│   ├── app/
│   │   ├── api/                    # v1 前台接口、staff 后台接口
│   │   ├── middleware/             # JWT/限流/参数校验/隧道等装饰器
│   │   ├── utils/                  # SM2/SM3/SM4、tunnel、db、auth 等
│   │   └── certs/server/           # ca_local.crt、server.crt、server.key
│   └── docs/第4周验收/             # 联调记录、登录成功截图
└── v1-zhognshe-rebuild-3-vue/      # Vue3 前端
    └── src/
        ├── request.js              # Axios 实例与拦截器（默认指向 HTTPS 后端）
        └── utils/sm-tunnel.js      # 前端隧道加密封装（内置默认密钥，.env 可选覆盖）
```

## 环境要求

- Windows，全部服务运行在本机 127.0.0.1，无需内网穿透
- Python 3.12+
- Node.js 18+（开发机实测 v24.16.0）
- MySQL 8+/9+（开发机实测 9.0.1，端口 3306）

## 快速开始

### 1. 准备数据库

启动本机 MySQL，创建数据库（表结构在后端首次启动时自动创建）：

```sql
CREATE DATABASE secure_ecommerce DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 2. 启动后端（HTTPS）

```powershell
cd 后端flask
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

copy .env.example .env
# 编辑 .env：至少填写 DB_PASSWORD（本机 MySQL 密码），
# SECRET_KEY / JWT_SECRET 建议替换为随机值（模板内的 SM2 密钥可直接用于本地 Demo）

.\.venv\Scripts\python.exe run.py
```

启动后服务地址为 `https://127.0.0.1:5000`。

### 3. 信任本地 CA（仅首次）

后端使用自签的本地 CA，把它导入当前用户受信任根，浏览器才不会拦截：

```powershell
certutil -user -addstore -f Root "后端flask\app\certs\server\ca_local.crt"
```

导入后访问 `https://127.0.0.1:5000/` 应直接显示 `Hello, World!`。

### 4. 启动前端并登录

```powershell
cd v1-zhognshe-rebuild-3-vue
npm install
npm run dev
```

浏览器打开 `http://127.0.0.1:5173/user/login`，输入账号密码（开发机联调账号 `zhangsan / 123456`，角色选“用户”），登录成功后跳转首页，右上角与个人中心可正常使用。

> 前端代码内置的默认地址（`https://127.0.0.1:5000`）与隧道密钥已和后端 demo 配置对齐，无需创建前端 `.env`；需要覆盖时再添加 `.env`（含 `VITE_API_BASE_URL`、`VITE_SM2_FLASK_PUBLIC_KEY`、`VITE_SM2_VUE_PRIVATE_KEY`，`.env` 按仓库规则不入库）。

## 验收复现顺序（第4周 6 类验证）

1. **正常加解密**：按上面步骤真实登录一次，页面提示“登录成功”并拿到 token；详细过程见 [后端flask/docs/第4周验收/联调记录.md](后端flask/docs/第4周验收/联调记录.md)。
2. **会话密钥与 Nonce 每次不同**：联调记录第 4 节（后端 50 次、前端 20 次全部唯一）。
3. **密文篡改被拒绝**：在隧道测试中改动 `data` 字段后重发，后端返回 `TUNNEL_BODY_DECRYPT_FAILED`（HTTP 400）。
4. **重复请求被拒绝**：同一请求体重放，返回 `TUNNEL_REPLAY`（HTTP 409）。
5. **过期请求被拒绝**：时间戳超出 ±5 分钟窗口，返回 `TUNNEL_TS_EXPIRED`（HTTP 401）。
6. **抓包无明文**：抓包样例见仓库根目录 `userlogin抓包样例截图.png`，请求体只有 `{"env","data"}` 两个 base64 字段，无用户名/密码明文。

后端隧道自测可一键复现 3/4/5 类机制：

```powershell
cd 后端flask
.\.venv\Scripts\python.exe -m app.utils.tunnel
```

## 说明

- `.env` 含本机数据库口令与私钥，已通过 `.gitignore` 忽略，仓库只保留 `.env.example` 模板。
- 证书登录（客户端 SM2 证书）、支付等其它接口的证书/OpenSSL 配置按各模块文档单独说明，不影响第 4 周登录隧道的验收。
