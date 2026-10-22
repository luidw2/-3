"""
OpenSSL 子进程统一调用封装。

解决四件事：
  1. 可执行文件路径校验（OPENSSL_PATH 不允许是任意程序）
  2. 敏感入参校验（口令等，禁止以 - 开头 / 控制字符 / 空格）
  3. 口令经 stdin 传递，不出现在命令行
  4. 统一超时与错误类型
"""
import os
import re
import shutil
import subprocess

from dotenv import load_dotenv

load_dotenv()

# 白名单：字母数字 + 常见的口令允许符号
_SAFE_ARG = re.compile(r'^[A-Za-z0-9_\-.,:@#!*+=]{0,128}$')


class OpenSSLError(RuntimeError):
    """OpenSSL 调用失败（启动失败 / 超时 / 返回非 0）"""


# ---------------------------------------------------------------- 路径校验
def get_openssl_path() -> str:
    """
    解析并校验 OpenSSL 可执行文件路径。
    优先级：OPENSSL_PATH（.env）> PATH 中的 openssl。
    任何一种来源都必须通过校验，否则抛错。
    """
    raw = (os.getenv('OPENSSL_PATH') or '').strip().strip('"')

    if raw:
        if not os.path.isabs(raw):
            raise OpenSSLError(f'OPENSSL_PATH 必须是绝对路径：{raw}')
        if not os.path.isfile(raw):
            raise OpenSSLError(f'OPENSSL_PATH 指向的文件不存在：{raw}')
        if not os.access(raw, os.X_OK):
            raise OpenSSLError(f'OPENSSL_PATH 指向的文件不可执行：{raw}')
        real = os.path.realpath(raw)
        if not os.path.basename(real).lower().startswith('openssl'):
            raise OpenSSLError(f'OPENSSL_PATH 指向的不是 openssl：{real}')
        return real

    found = shutil.which('openssl')
    if not found:
        raise OpenSSLError(
            '未配置 OPENSSL_PATH，且 PATH 中找不到 openssl。'
            '请在 .env 中设置 OPENSSL_PATH 为 openssl.exe 的绝对路径。'
        )
    return os.path.realpath(found)


# ---------------------------------------------------------------- 入参校验
def validate_secret(value: str, name: str = '口令', max_len: int = 128) -> str:
    """
    校验会进入 openssl 参数的敏感输入。

    拒绝：非字符串 / 空 / 超长 / 以 - 开头 / 含控制字符或空格引号等。
    通过则原样返回，方便链式调用。
    """
    if not isinstance(value, str) or not value:
        raise ValueError(f'{name}不能为空')
    if len(value) > max_len:
        raise ValueError(f'{name}长度超过 {max_len} 字符')
    if value.startswith('-'):
        raise ValueError(f'{name}不能以 - 开头')
    if not _SAFE_ARG.match(value):
        raise ValueError(f'{name}含非法字符，仅允许字母数字和 _-.,:@#!*+=')
    return value


# ---------------------------------------------------------------- 执行
def run_openssl(args, *, stdin_data=None, timeout=30, check=True):
    """
    以列表参数执行 OpenSSL。

    args       : list[str]，不含可执行文件本身
    stdin_data : 写入子进程 stdin 的文本（口令走这里）
    timeout    : 超时秒数
    check      : True 时返回码非 0 抛 OpenSSLError

    绝不使用 shell=True；显式传入最小环境变量。
    """
    if not isinstance(args, (list, tuple)) or not args:
        raise ValueError('args 必须是非空列表')
    for i, a in enumerate(args):
        if not isinstance(a, str):
            raise ValueError(f'args[{i}] 必须是字符串，实际为 {type(a).__name__}')
        if '\x00' in a:
            raise ValueError(f'args[{i}] 含 NUL 字符')

    cmd = [get_openssl_path(), *args]

    # 只给最小环境变量，不整体继承 os.environ
    env = {
        'PATH': os.environ.get('PATH', ''),
        'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
        'TEMP': os.environ.get('TEMP', ''),
        'TMP': os.environ.get('TMP', ''),
    }

    try:
        result = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,      # 显式声明，防止日后被改成 True
            env=env,
        )
    except subprocess.TimeoutExpired:
        raise OpenSSLError(f'OpenSSL 执行超时（{timeout}s）：{args[0]}')
    except FileNotFoundError:
        raise OpenSSLError(f'找不到 OpenSSL 可执行文件：{cmd[0]}')
    except OSError as e:
        raise OpenSSLError(f'OpenSSL 启动失败：{e}')

    if check and result.returncode != 0:
        raise OpenSSLError(
            f'OpenSSL 执行失败（exit={result.returncode}）：{args[0]}\n'
            f'stderr: {(result.stderr or "").strip()}'
        )
    return result