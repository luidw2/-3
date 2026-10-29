# 第9周性能测试环境

本目录提供可直接运行的登录、商品查询、下单JMeter场景。2026-10-29已在本机完成小规模运行验证；这些结果用于确认环境和脚本可用，不是正式性能基线，也不证明优化达到20%。

后续已增加独立数据库和三轮统一版本基线流程。P0-2至P0-5的当前入口为 [环境说明](../基线报告/环境说明.md)，整批执行命令为 `python ./performance/run_baseline.py`。以下单次调试命令固定使用独立端口5001；原5000服务和此前冒烟结果保留。

## 本机准备状态

- 后端 `.env` 的 `OPENSSL_PATH` 已改为 `C:/Program Files/OpenSSL-Win64/bin/openssl.exe`；`.env` 不入Git。
- 工作区根目录 `.local-tools/` 已安装并校验 Temurin Java 21.0.12.1+1 JRE、Apache JMeter 5.6.3、Bouncy Castle 1.86。版本、来源和校验值见 `tools-lock.json`。
- 后端监听 `http://127.0.0.1:5000/`，关闭debug和自动重载，保留应用层加密隧道。当前采用Flask本地开发服务器；正式对照测试需固定相同的服务启动方式。
- 创建20个 `perf9_user_001` 至 `perf9_user_020` 专用用户、1个 `perf9_seller` 专用商户、100个 `perf9_product_0001` 至 `perf9_product_0100` 商品及专用用户的购物车。现有用户和商品保留。
- 账号密码随机生成，CSV和客户端密钥配置存于 `.local/`，被Git忽略。不要将这些文件上传到公开仓库。

## 运行方式

以下命令均在 `-3` 仓库目录执行。无需修改系统Java或PATH。

首次换机器时，先在Python环境安装项目实际使用的依赖，并配置后端 `.env` 中的数据库及SM2密钥。本次没有按原 `requirements.txt` 全量安装：其中含其他环境的工具包，且本机已安装库与该文件部分版本不同。本机验证记录列出了实际使用版本。

```powershell
# 当前机器已完成；其他机器可按锁定版本下载并校验工具。
python ./performance/setup_tools.py

# 幂等准备专用账号和商品。需要清理失败测试遗留的专用购物车商品时加 --reset-carts。
# 不删除已有订单，也不修改普通业务用户。
python ./performance/database_fixture.py init
python ./performance/seed_data.py --database perf9_baseline --users 20 --products 100
# 仅首次生成；已有快照时不要重复生成，使用database_fixture.py reset恢复。
python ./performance/database_fixture.py snapshot

# 服务已经运行时不用重复执行。该脚本遇到端口占用会停止，不会杀掉已有服务。
powershell -NoProfile -ExecutionPolicy Bypass -File ./performance/start-backend.ps1 -Port 5001 -Database perf9_baseline

# 默认2线程、2轮，每个循环请求前等待1500毫秒。
powershell -NoProfile -ExecutionPolicy Bypass -File ./performance/run-jmeter.ps1 -Scenario login -Port 5001
powershell -NoProfile -ExecutionPolicy Bypass -File ./performance/run-jmeter.ps1 -Scenario products -Port 5001
powershell -NoProfile -ExecutionPolicy Bypass -File ./performance/run-jmeter.ps1 -Scenario order -Port 5001
```

`run-jmeter.ps1` 可指定 `-Threads`、`-Loops`、`-Ramp`、`-ThinkMs`、`-ServerHost`、`-Port`、`-Protocol`、`-OutputDirectory`。输出目录若已存在则拒绝覆盖。未指定时每次产生独立目录 `.local/results/<时间>-<场景>/`，包含：

- `run.json`：运行参数、代码提交号和未提交变更说明。
- `results.jtl`：全部准备、业务及回查请求的原始结果；不保存正文和令牌。
- `html/index.html`：只统计 `business-*` 请求的HTML报告；准备登录、加购物车及订单回查不会混入业务p95。
- `jmeter.log`：JMeter运行日志。

脚本要求业务采样数恰好为 `线程数 × 循环数`，且全部准备/业务/回查样本成功，否则返回失败。JMeter进程正常退出但断言失败，也不会被判作通过。

## 三个场景的含义

| 场景 | 准备与执行 | 成功校验 |
| --- | --- | --- |
| login | 每线程固定专用账号，每次请求重新生成SM4 key/IV、Nonce和时间戳，经SM2封装后登录 | HTTP200；解密响应后code=0，access_token存在 |
| products | 每线程加密登录一次；循环GET商品列表，无GET请求体 | HTTP200；code=0；商品列表与总量有效 |
| order | 每线程加密登录一次；每轮加入指定商品1件，再下单，最后按订单ID回查 | 加车code=200且数量1；下单code=200、有效订单ID、匹配商品/数量/总额；订单回查成功 |

每个线程固定使用CSV对应行的账号，不会在线程间共享购物车。脚本同时保存在 `plans/` 和原有 `基线报告/` 对应目录；`generate_plans.py` 是生成源，修改场景时运行它同步。旧的 `Test Plan.jmx`、`Product_Api_Test.jmx` 和历史JTL/HTML保持原样，仅作为历史资料，不作为新版入口。修改后的同名JMX不用于解释旧报告的运行条件。

## 已知口径与负载设置

1. 当前协议是项目现有的 **SM2 + SM4-CBC**，不是课件要求的GCM。本次为准备环境而保留协议；未来完成GCM后必须同步脚本并重新建立正式基线。
2. 当前访问本机HTTP端口，不构成HTTPS验收。需要测HTTPS时，应先配置真实HTTPS入口，再用相应host/port/protocol运行，不可只改协议参数。
3. 加密在JMeter原生Groovy预处理器中执行，使用Bouncy Castle，不启动额外Python进程或代理。HTTP采样耗时包含后端解密/业务/加密，但不包含客户端预处理和响应断言耗时；完整线程循环时间还包含这些开销及定时等待。
4. 下单、加车、订单回查共享当前限流中间件的IP计数，每分钟总计最多100次。默认2线程及1500毫秒等待用于低负载验证；没有关闭限流。20线程时建议先用 `-ThinkMs 15000` 并观察实际请求量。`-ThinkMs 0` 只用于很少请求的冒烟验证，持续运行会触发429。429会计入失败，不会被隐藏。
5. 下单会生成真实的专用测试订单并清空专用购物车；不会触发支付。独立基线库统一用 `database_fixture.py reset` 恢复快照。若只清购物车，必须显式指定 `seed_data.py --database perf9_baseline --reset-carts`，避免默认连接另一个库。不要在整批测试运行时重置或seed。
6. 增加线程前要有足够的专用账号。更改数据量、服务模式、协议、线程或定时器后，应重新记录基线，不能与旧配置直接计算改善率。
7. `.local/` 中的结果和凭据一起被忽略；正式提交测试证据时应审核后将JTL、环境说明、监控数据和HTML报告复制到专门的验收目录，不能直接上传整个 `.local/`。

## 当前检查结果

见 `环境就绪验证.md`。本次只验证场景能跑通，正式基线仍需固定数据快照、预热、测试时长、监控采集方法和前后版本，再做足够样本的重复测试。

工具来源：[Apache JMeter](https://downloads.apache.org/jmeter/)、[Eclipse Adoptium](https://adoptium.net/installation/ci-scripts)、[Bouncy Castle](https://www.bouncycastle.org/download/bouncy-castle-java/)。
