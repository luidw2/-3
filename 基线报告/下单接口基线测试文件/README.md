# 下单接口测试交付

入口：本目录 `Test_user_order.jmx`；同步副本为 `performance/plans/order.jmx`，生成源为 `performance/generate_plans.py`。运行依赖、协议、参数和数据重置方法见 [环境说明](../环境说明.md)。

新版统一版本基线保存在 [baseline/20261029-100809/order](../baseline/20261029-100809/order/)。每个run目录包含：

- `warmup/`：预热JTL、监控CSV、HTML及运行记录。
- `measurement/`：正式JTL、监控CSV、HTML、业务指标和运行记录。
- `before-warmup.json`、`before-measurement.json`：恢复到同一初始快照的校验。
- `after-measurement.json`：订单、明细和购物车数量复核。

场景顺序：每线程独立账号 → 加密登录 → 每轮加入1件指定商品 → 下单 → 校验业务码、订单ID、商品、数量和金额 → 读取订单详情确认入库。准备及回查请求不混入business-order的性能统计，但任一步失败会使该轮失败。

所有正式数据集中归档，避免复制同一份原始证据后出现版本分歧；本目录通过路径直接定位下单的JTL、HTML和监控交付物。
