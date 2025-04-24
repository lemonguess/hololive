import json
import os
import time
import uuid
import logging
import httpx
logger = logging.getLogger(__name__)



def get_uuid():
    return uuid.uuid4().hex


def json_loads(json_str):
    try:
        if isinstance(json_str, dict):  # 如果已经是字典，直接返回
            return json_str
        elif isinstance(json_str, list):  # 如果已经是列表，直接返回
            return json_str
        elif isinstance(json_str, str):
            return json.loads(json_str)
    except:
        logger.error("Could not decode json: %s", json_str)
        return {}
def replace_keys(obj):
    """递归替换所有字典键中的点为下划线"""
    if isinstance(obj, dict):
        return {key.replace('.', '_'): replace_keys(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [replace_keys(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(replace_keys(item) for item in obj)
    return obj



def generator_rules(rules_str: str, tokens, times):
    for message in rules_str:
        if "\n" in message:
            newlines_count = message.count("\n")
            yield {
                "event": "add",
                "data": json.dumps({"msg": message[:message.find("\n")]}, ensure_ascii=False)
            }
            for _ in range(newlines_count):
                yield {
                    "event": "newline",
                    "data": "\\n"
                }
        else:
            yield {
                "event": "add",
                "data": json.dumps({"msg": message}, ensure_ascii=False)
            }
    yield {"event": "finish", "data": json.dumps(
        {"prompt_tokens": tokens.prompt_tokens if tokens else 0, "completion_tokens": tokens.completion_tokens if tokens else 0,
         "total_tokens": tokens.total_tokens if tokens else 0, "duration": get_timestamp() - times}, ensure_ascii=False)}

def get_project_base_directory(*args):
    PROJECT_BASE = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                os.pardir,
                # os.pardir,
            )
        )

    if args:
        return os.path.join(PROJECT_BASE, *args)
    return PROJECT_BASE



def get_file_type(filename):
    ext = filename.split('.')[-1].lower() if '.' in filename else ''

    type_map = {
    # 文本类
    'txt': '纯文本', 'md': 'Markdown文档', 'log': '日志文件', 'csv': 'CSV数据',
    'json': 'JSON数据', 'xml': 'XML文件', 'yaml': 'YAML配置', 'ini': '配置文件',

    # 开发类
    'py': 'Python脚本', 'js': 'JavaScript', 'java': 'Java代码', 'cpp': 'C++代码',
    'html': '网页文件', 'css': '样式表', 'sh': 'Shell脚本', 'sql': 'SQL脚本',
    'ipynb': 'Jupyter Notebook', 'dockerfile': 'Docker配置',

    # 文档类
    'pdf': 'PDF文档', 'docx': 'Word文档', 'pptx': 'PPT演示稿', 'xlsx': 'Excel表格',
    'odt': 'OpenDocument文本', 'epub': '电子书', 'xls': 'Excel表格',

    # 图像类
    'jpg': 'JPEG图像', 'png': 'PNG图像', 'gif': 'GIF动图', 'webp': 'WebP图像',
    'svg': '矢量图', 'psd': 'Photoshop文件', 'ico': '图标文件',

    # 音频类
    'mp3': 'MP3音频', 'wav': 'WAV音频', 'flac': '无损音频', 'aac': 'AAC音频',

    # 视频类
    'mp4': 'MP4视频', 'avi': 'AVI视频', 'mov': 'QuickTime视频', 'mkv': 'Matroska视频',
    'flv': 'Flash视频',

    # 压缩归档类
    'zip': 'ZIP压缩包', 'rar': 'RAR压缩包', 'tar': 'TAR归档', 'gz': 'GZIP压缩文件',
    '7z': '7-Zip压缩包',

    # 系统类
    'exe': '可执行文件', 'dll': '动态链接库', 'sys': '系统驱动', 'msi': '安装程序包',

    # 虚拟化类
    'iso': '光盘镜像', 'vmdk': '虚拟机磁盘', 'ova': '虚拟设备模板',

    # 数据库类
    'db': '数据库文件', 'sqlite': 'SQLite数据库', 'mdb': 'Access数据库',

    # 3D建模类
    'stl': '3D模型文件', 'obj': 'Wavefront模型', 'fbx': 'Autodesk模型',

    # 字体类
    'ttf': 'TrueType字体', 'otf': 'OpenType字体', 'woff': '网页字体'
}
    return type_map.get(ext, '未知类型')