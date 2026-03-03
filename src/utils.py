import os
import sys
import tempfile
import filelock
from pathlib import Path


def is_admin() -> bool:
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def get_app_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


def parse_command_args() -> list:
    args = sys.argv[1:]
    paths = []
    
    for arg in args:
        path = Path(arg)
        if path.exists():
            paths.append(str(path.absolute()))
    
    return paths


def ensure_single_instance(app_name: str = "FileCleaner") -> bool:
    import ctypes
    
    app_mutex = ctypes.windll.kernel32.CreateMutexW(
        None, False, app_name
    )
    last_error = ctypes.windll.kernel32.GetLastError()
    
    return last_error != 183


def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


# --- 多文件聚合相关 ---

_AGGREGATION_DIR = os.path.join(tempfile.gettempdir(), "FileCleaner")
_AGGREGATION_FILE = os.path.join(_AGGREGATION_DIR, "pending_paths.txt")
_LOCK_FILE = os.path.join(_AGGREGATION_DIR, "instance.lock")


def _ensure_agg_dir():
    os.makedirs(_AGGREGATION_DIR, exist_ok=True)


def get_instance_lock() -> filelock.FileLock:
    """获取实例文件锁对象。"""
    _ensure_agg_dir()
    return filelock.FileLock(_LOCK_FILE, timeout=0)


def write_paths_to_aggregation_file(paths: list):
    """将路径追加写入聚合文件（线程安全）。"""
    _ensure_agg_dir()
    with open(_AGGREGATION_FILE, "a", encoding="utf-8") as f:
        for p in paths:
            f.write(p + "\n")


def read_and_clear_aggregation_file() -> list:
    """读取聚合文件中所有路径并清空文件，返回去重后的列表。"""
    if not os.path.exists(_AGGREGATION_FILE):
        return []
    with open(_AGGREGATION_FILE, "r", encoding="utf-8") as f:
        lines = f.read().strip().splitlines()
    # 清空
    with open(_AGGREGATION_FILE, "w", encoding="utf-8") as f:
        f.write("")
    # 去重且保持顺序
    seen = set()
    result = []
    for line in lines:
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            result.append(line)
    return result
