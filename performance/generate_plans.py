"""Generate portable replacement plans; historical JTL/HTML remain unchanged."""
from pathlib import Path
from xml.etree import ElementTree as E

ROOT = Path(__file__).resolve().parents[1]


def prop(parent, name, value, tag='stringProp'):
    return E.SubElement(parent, tag, name=name, **{}).__setattr__('text', str(value))


def node(tree, tag, name, gui=None):
    e = E.SubElement(tree, tag, guiclass=gui or tag, testclass=tag, testname=name, enabled='true')
    child = E.SubElement(tree, 'hashTree')
    return e, child


def script(tree, tag, name, file=None, code=''):
    gui = {'JSR223Sampler':'TestBeanGUI','JSR223Assertion':'TestBeanGUI','JSR223PreProcessor':'TestBeanGUI'}[tag]
    e, child = node(tree, tag, name, gui)
    for key, value in {'scriptLanguage':'groovy','parameters':'','filename':file or '',
                       'cacheKey':'true','script':code}.items():
        prop(e, key, value)
    return child


def http(tree, name, path, method='GET', body=None, encrypted=False):
    e, child = node(tree, 'HTTPSamplerProxy', name, 'HttpTestSampleGui')
    arg = E.SubElement(e, 'elementProp', name='HTTPsampler.Arguments', elementType='Arguments')
    collection = E.SubElement(arg, 'collectionProp', name='Arguments.arguments')
    if body is not None:
        a = E.SubElement(collection,'elementProp',name='',elementType='HTTPArgument')
        prop(a,'HTTPArgument.always_encode','false','boolProp')
        prop(a,'Argument.value',body)
        prop(a,'Argument.metadata','=')
    for k,v in {'HTTPSampler.domain':'${__P(host,127.0.0.1)}',
        'HTTPSampler.port':'${__P(port,5000)}','HTTPSampler.protocol':'${__P(protocol,http)}',
        'HTTPSampler.path':path,'HTTPSampler.method':method,'HTTPSampler.contentEncoding':'UTF-8',
        'HTTPSampler.connect_timeout':'5000','HTTPSampler.response_timeout':'30000'}.items():prop(e,k,v)
    for k,v in {'HTTPSampler.use_keepalive':'true','HTTPSampler.follow_redirects':'false',
                 'HTTPSampler.postBodyRaw':str(body is not None).lower()}.items():prop(e,k,v,'boolProp')
    if encrypted:
        script(child,'JSR223PreProcessor','encrypt-login','${__P(perf_dir)}/scripts/login-request.groovy')
    script(child,'JSR223Assertion','verify-business','${__P(perf_dir)}/scripts/check-response.groovy')


def generate(kind, path):
    root=E.Element('jmeterTestPlan',version='1.2',properties='5.0',jmeter='5.6.3')
    tree=E.SubElement(root,'hashTree')
    plan, pt=node(tree,'TestPlan','Week9 '+kind,'TestPlanGui')
    prop(plan,'TestPlan.serialize_threadgroups','false','boolProp')
    E.SubElement(E.SubElement(plan,'elementProp',name='TestPlan.user_defined_variables',elementType='Arguments'),
                 'collectionProp',name='Arguments.arguments')
    tg, tt=node(pt,'ThreadGroup','isolated-users','ThreadGroupGui')
    prop(tg,'ThreadGroup.on_sample_error','stopthread')
    loop=E.SubElement(tg,'elementProp',name='ThreadGroup.main_controller',elementType='LoopController',
                     guiclass='LoopControlPanel',testclass='LoopController',testname='Thread iterations',enabled='true')
    prop(loop,'LoopController.continue_forever','false','boolProp');prop(loop,'LoopController.loops','1')
    prop(tg,'ThreadGroup.num_threads','${__P(threads,2)}')
    prop(tg,'ThreadGroup.ramp_time','${__P(ramp,1)}')
    prop(tg,'ThreadGroup.scheduler','false','boolProp')
    headers,ht=node(tt,'HeaderManager','JSON and access token','HeaderPanel')
    hc=E.SubElement(headers,'collectionProp',name='HeaderManager.headers')
    for key,value in [('Content-Type','application/json'),('Authorization','Bearer ${access_token}')]:
        h=E.SubElement(hc,'elementProp',name='',elementType='Header')
        prop(h,'Header.name',key);prop(h,'Header.value',value)
    script(tt,'JSR223Sampler','prepare-fixture',code='''
import java.nio.file.Files
import java.nio.file.Paths
def rows = Files.readAllLines(Paths.get(props.getProperty('users_file')), java.nio.charset.StandardCharsets.UTF_8)
int index = ctx.getThreadNum() + 1
if (index >= rows.size()) throw new IllegalArgumentException('Not enough dedicated users')
def fields = rows[index].split(',')
vars.put('username',fields[0]); vars.put('password',fields[1]); vars.put('product_id',fields[2])
vars.put('access_token','')
SampleResult.setResponseCode('200'); SampleResult.setResponseMessage('Dedicated fixture assigned')
SampleResult.setSuccessful(true)
''')
    if kind!='login':http(tt,'prepare-login','/user/login','POST','${login_wire}',True)
    le, lt=node(tt,'LoopController','measured-iterations','LoopControlPanel')
    prop(le,'LoopController.continue_forever','false','boolProp')
    prop(le,'LoopController.loops','${__P(loops,2)}')
    timer,_=node(lt,'ConstantTimer','per-request pacing','ConstantTimerGui')
    prop(timer,'ConstantTimer.delay','${__P(think_ms,1500)}')
    if kind=='login':http(lt,'business-login','/user/login','POST','${login_wire}',True)
    elif kind=='products':http(lt,'business-products','/user/products/profile?page=1&size=20&keyword=perf9_product_')
    else:
        http(lt,'prepare-cart','/user/add_to_shopping_car/${product_id}','POST','{"quantity":1}')
        http(lt,'business-order','/user/create_order','POST','{}')
        http(lt,'verify-order','/user/profile_order/${order_id}')
    E.indent(root,space='  ')
    path.parent.mkdir(parents=True,exist_ok=True)
    E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)


if __name__=='__main__':
    targets={'login':ROOT/'基线报告/登录接口基线测试文件/Test_user_login.jmx',
        'products':ROOT/'基线报告/商品查看接口基线测试文件/Test_user_product_profile.jmx',
        'order':ROOT/'基线报告/下单接口基线测试文件/Test_user_order.jmx'}
    for kind,path in targets.items():
        generate(kind,path)
        generate(kind,ROOT/'performance'/'plans'/f'{kind}.jmx')
        print('Generated',kind)
