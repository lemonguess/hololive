import datetime
from typing import Any, Dict

class Serializer:
    @staticmethod
    def serialize(obj: Any) -> Dict[str, Any]:
        """
        将对象序列化为字典，处理 datetime 类型字段的序列化。
        
        :param obj: 需要序列化的对象
        :return: 序列化后的字典
        """
        if isinstance(obj, dict):
            return {key: Serializer.serialize(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [Serializer.serialize(item) for item in obj]
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return {key: Serializer.serialize(value) for key, value in obj.__dict__.items() if not key.startswith('_')}
        else:
            return obj