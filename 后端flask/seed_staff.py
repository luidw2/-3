# ============================================================================
# seed_staff.py —— 后台演示账号初始化脚本（管理员/审计员）
# 运行方式（在后端flask目录下）：
#   .venv\Scripts\python.exe seed_staff.py
# 作用：1) 调用 db.init_db() 创建缺失的表（含 staff 表，只建新表不影响老表）；
#       2) 创建后台演示账号 admin1(管理员) / audit1(审计员)。
# 说明：脚本可重复执行（账号已存在时 create_staff 返回 None，不报错）。
# ============================================================================
from app.utils import db


def main():
    db.init_db()
    a = db.create_staff('admin1', 'Admin@123456', role='admin')
    b = db.create_staff('audit1', 'Audit@123456', role='auditor')
    print('admin1(管理员):', '创建成功' if a else '已存在或创建失败')
    print('audit1(审计员):', '创建成功' if b else '已存在或创建失败')


if __name__ == '__main__':
    main()
