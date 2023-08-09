import sys

from loguru import logger as _logger
from pathlib import Path


def get_project_root():
    """find the root dir"""
    current_path = Path.cwd()
    while True:
        if (
            (current_path / ".git").exists()
            or (current_path / ".project_root").exists()
            or (current_path / ".gitignore").exists()
        ):
            return current_path
        parent_path = current_path.parent
        if parent_path == current_path:
            raise Exception("Project root not found.")
        current_path = parent_path


def define_log_level(print_level="INFO", logfile_level="DEBUG"):
    project_root = get_project_root()
    """adjust log-level above level"""
    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(project_root / "logs/log.txt", level=logfile_level)
    return _logger


logger = define_log_level()
