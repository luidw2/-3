import groovy.json.JsonOutput
import java.security.SecureRandom
import java.security.Security
import org.bouncycastle.jce.provider.BouncyCastleProvider
import org.bouncycastle.asn1.gm.GMNamedCurves
import org.bouncycastle.crypto.params.ECDomainParameters
import org.bouncycastle.crypto.params.ECPublicKeyParameters
import org.bouncycastle.crypto.params.ParametersWithRandom
import org.bouncycastle.crypto.engines.SM2Engine
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec
import javax.crypto.spec.IvParameterSpec

if (Security.getProvider('BC') == null) Security.addProvider(new BouncyCastleProvider())
def random = new SecureRandom()
def bytes = { int n -> byte[] b = new byte[n]; random.nextBytes(b); b }
byte[] key = bytes(16), iv = bytes(16), nonce = bytes(16)
def blob = JsonOutput.toJson([key:key.encodeHex().toString(), iv:iv.encodeHex().toString(),
    nonce:nonce.encodeHex().toString(), ts:System.currentTimeMillis()]).getBytes('UTF-8')
def curve = GMNamedCurves.getByName('sm2p256v1')
def domain = new ECDomainParameters(curve.curve, curve.g, curve.n, curve.h)
String pub = props.getProperty('sm2_server_public')
if (pub.length() == 128) pub = '04' + pub
def engine = new SM2Engine(SM2Engine.Mode.C1C2C3)
engine.init(true, new ParametersWithRandom(new ECPublicKeyParameters(curve.curve.decodePoint(pub.decodeHex()), domain), random))
byte[] envelope = engine.processBlock(blob, 0, blob.length)
def cipher = Cipher.getInstance('SM4/CBC/PKCS7Padding', 'BC')
cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, 'SM4'), new IvParameterSpec(iv))
byte[] body = JsonOutput.toJson([username:vars.get('username'),password:vars.get('password'),role:'user']).getBytes('UTF-8')
vars.put('login_wire', JsonOutput.toJson([env:envelope.encodeBase64().toString(),data:cipher.doFinal(body).encodeBase64().toString()]))
