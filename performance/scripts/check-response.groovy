import groovy.json.JsonSlurper
import java.security.Security
import org.bouncycastle.jce.provider.BouncyCastleProvider
import org.bouncycastle.asn1.gm.GMNamedCurves
import org.bouncycastle.crypto.params.ECDomainParameters
import org.bouncycastle.crypto.params.ECPrivateKeyParameters
import org.bouncycastle.crypto.engines.SM2Engine
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec
import javax.crypto.spec.IvParameterSpec

try {
    assert prev.getResponseCode() == '200': 'Unexpected HTTP status'
    def json = new JsonSlurper()
    def obj = json.parseText(prev.getResponseDataAsString())
    String label = prev.getSampleLabel()
    if (label.endsWith('login')) {
        assert obj.env && obj.data: 'Encrypted response missing'
        if (Security.getProvider('BC') == null) Security.addProvider(new BouncyCastleProvider())
        def curve = GMNamedCurves.getByName('sm2p256v1')
        def domain = new ECDomainParameters(curve.curve, curve.g, curve.n, curve.h)
        def engine = new SM2Engine(SM2Engine.Mode.C1C2C3)
        engine.init(false, new ECPrivateKeyParameters(new BigInteger(props.getProperty('sm2_client_private'),16), domain))
        byte[] env = obj.env.decodeBase64()
        def blob = json.parseText(new String(engine.processBlock(env,0,env.length), 'UTF-8'))
        assert Math.abs(System.currentTimeMillis() - (blob.ts as long)) <= 300000: 'Expired response'
        def cipher = Cipher.getInstance('SM4/CBC/PKCS7Padding','BC')
        cipher.init(Cipher.DECRYPT_MODE,new SecretKeySpec(blob.key.decodeHex(),'SM4'),new IvParameterSpec(blob.iv.decodeHex()))
        obj = json.parseText(new String(cipher.doFinal(obj.data.decodeBase64()),'UTF-8'))
        assert obj.code == 0 && obj.data?.access_token: 'Login business failure'
        vars.put('access_token',obj.data.access_token as String)
    } else if (label == 'business-products') {
        assert obj.code == 0 && obj.data?.items instanceof List && obj.data.total > 0: 'Product query business failure'
        assert obj.data.items.size() > 0: 'Empty product page'
    } else if (label == 'prepare-cart') {
        assert obj.code == 200 && obj.data?.cart_item_id && obj.data.quantity == 1: 'Cart preparation failed or dirty cart'
    } else if (label == 'business-order') {
        assert obj.code == 200 && obj.data?.order_id && obj.data.items?.size() == 1: 'Order business failure'
        assert obj.data.items[0].product_id == (vars.get('product_id') as int): 'Wrong product in order'
        assert obj.data.items[0].quantity == 1 && obj.data.total_price > 0: 'Wrong quantity or total'
        vars.put('order_id',obj.data.order_id.toString())
    } else if (label == 'verify-order') {
        assert obj.code == 200 && obj.data?.order_id == (vars.get('order_id') as int): 'Order read-back failed'
    }
} catch (Throwable error) {
    AssertionResult.setFailure(true)
    // Do not copy responses (tokens), passwords or cryptographic keys into results.
    AssertionResult.setFailureMessage('Business verification failed: ' + error.class.simpleName)
    log.warn('Business verification failed for {} ({})',prev.getSampleLabel(),error.class.simpleName)
}
