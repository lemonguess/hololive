import os
from configparser import ConfigParser
from dotenv import load_dotenv
load_dotenv()

class Configuration:
    def __init__(self, config_dict):
        for key, value in config_dict.items():
            if isinstance(value, dict):
                setattr(self, key, Configuration(value))  # 如果 value 是字典，递归创建 Configuration 实例
            else:
                setattr(self, key, value)


def get_config_parser() -> Configuration:
    config = ConfigParser()
    config_base_path = "config/"
    if os.getenv("RUNTIME_ENV") == "pro":
        config_path = os.path.join(config_base_path, 'conf_pro.ini')
    elif os.getenv("RUNTIME_ENV") == "dev":
        config_path = os.path.join(config_base_path, 'conf.ini')
    else:
        raise ValueError("RUNTIME_ENV is not set to 'pro' or 'dev'")
    config.read(config_path)
    config_data = dict()
    for section in config.sections():
        config_dict = {key: config.get(section, key) for key in config.options(section)}
        config_data.update({section: config_dict})
    config_data = Configuration(config_data)
    return config_data


if __name__ == '__main__':
    data = get_config_parser()
    # {'redis_config': {'password': '', 'host': '118.31.112.25', 'port': '6379'}}
    print(data.redis_config.port)