"""资源路径管理"""

from pathlib import Path
from gsuid_core.data_store import get_res_path

# 插件数据根目录（gsuid_core 统一管理）
JRYS_PATH = get_res_path() / "JRYS"
JRYS_PATH.mkdir(parents=True, exist_ok=True)

# 背景图片目录（用户自行放置图片）
BG_IMAGE_PATH = JRYS_PATH / "bg"
BG_IMAGE_PATH.mkdir(parents=True, exist_ok=True)

# 用户运势缓存目录
CACHE_PATH = JRYS_PATH / "cache"
CACHE_PATH.mkdir(parents=True, exist_ok=True)

# 插件配置文件路径
CONFIG_PATH = JRYS_PATH / "config.json"

