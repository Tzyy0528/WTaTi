import shlex
import shutil
import subprocess
from pathlib import Path


def normalize_symbols(symbols):
    """返回排序去重后的元素符号。"""
    return tuple(sorted(set(symbols)))


def system_name(symbols):
    """根据元素符号生成稳定的体系名称。"""
    return "-".join(normalize_symbols(symbols))


def format_value(value):
    """将数值格式化为适合目录名的字符串。"""
    return f"{value:g}".replace("-", "m").replace(".", "p")


def find_existing_path(candidates):
    """从候选列表中返回第一个存在的路径。"""
    for candidate in candidates:
        if candidate is None:
            continue
        path = Path(candidate)
        if path.exists():
            return path.resolve()
    return None


def copy_once(src, dst):
    """仅当目标文件不存在时复制文件。"""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst)


def command_with_optional_module(cmd, module_name):
    """在需要时为命令添加 module load 包装。"""
    command_text = " ".join(shlex.quote(str(part)) for part in cmd)
    if module_name:
        command_text = (
            f"module load {shlex.quote(module_name)} && {command_text}"
        )
        return ["bash", "-lc", command_text], command_text
    return cmd, command_text


def run_logged_command(cmd, cwd, log_path, command_path=None, module_name=None):
    """在指定目录运行命令并将标准输出/错误写入日志。"""
    run_cmd, command_text = command_with_optional_module(cmd, module_name)
    if command_path is not None:
        command_path.write_text(command_text + "\n", encoding="utf-8")
    with open(log_path, "w", encoding="utf-8") as log:
        subprocess.run(run_cmd, cwd=cwd, stdout=log,
                       stderr=subprocess.STDOUT, text=True, check=True)
