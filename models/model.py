from models.enums import UserRoleType, ModelType
from models.base import Base
from sqlalchemy.types import TypeDecorator
from sqlalchemy import Column, Integer, String, Text, DateTime as BaseDateTime, JSON, UniqueConstraint
from datetime import datetime



class IntEnum(TypeDecorator):
    """
    整数枚举类型 主要用于状态等场景
    """
    impl = Integer
    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype
    def process_bind_param(self, value, dialect):
        """入库时调用此方法，返回的是枚举的value"""
        return value.value
    def process_result_value(self, value, dialect):
        """从数据库加载到内存时的值，返回的一个枚举实例"""
        return self._enumtype(value)

class StrEnum(TypeDecorator):
    """
    字符串枚举类型 主要用于状态等场景
    """
    impl = String
    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype
    def process_bind_param(self, value, dialect):
        """入库时调用此方法，返回的是枚举的value"""
        return value.value
    # def process_result_value(self, value, dialect):
    #     """从数据库加载到内存时的值，返回的一个枚举实例"""
    #     return self._enumtype(value)

class DateTime(TypeDecorator):
    """自定义 DateTime 类型，用于格式化时间字符串"""
    impl = BaseDateTime
    cache_ok = True  # 允许 SQLAlchemy 缓存该类型
    def process_bind_param(self, value, dialect):
        """写入数据库时的处理（保持 DateTime 类型）"""
        if isinstance(value, str):  # 处理可能的字符串输入
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value  # 直接返回 datetime 对象
    def process_result_value(self, value, dialect):
        """从数据库读取时的处理（转换为格式化字符串）"""
        if value is not None:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return None

class UsersModel(Base):
    """用户管理表"""
    __tablename__ = 'users'
    id = Column(String(255), primary_key=True, unique=True, nullable=False)
    role = Column(IntEnum(UserRoleType), nullable=False)  # 修改为 UserRoleType 枚举类型
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    nickname = Column(String(255), nullable=False)
    avatar = Column(Text)
    phone_num = Column(String(255))
    is_email_verified = Column(Integer, default=0)
    is_phone_verified = Column(Integer, default=0)
    is_deleted = Column(Integer, default=0)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)

class ProviderModel(Base):
    """供应商管理表"""
    __tablename__ = 'providers'
    id = Column(String(255), primary_key=True, unique=True, nullable=False)
    icon = Column(Text)
    name = Column(String(255), unique=True, nullable=False)
    name_zh = Column(String(255), nullable=False)
    description = Column(Text)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)

class ModelManagementModel(Base):
    """模型管理表"""
    __tablename__ = 'models'
    id = Column(String(255), primary_key=True, unique=True, nullable=False)  # 外键到 user_Providers.user_provider_uuid
    user_id = Column(String(255), nullable=False)
    provider_id = Column(String(255), nullable=False)  # 确保该值在 base_providers 表中存在
    type = Column(StrEnum(ModelType), nullable=False)  # 模型类型，使用枚举类 ModelType
    name = Column(String(255), nullable=False)  # 模型名称
    description = Column(Text)
    icon = Column(Text)
    base_url = Column(Text)
    config = Column(JSON)  # 模型配置，JSON类型
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    create_time = Column(DateTime, default=datetime.utcnow)  # 创建时间
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_id_name'),
    )

class AgentConfigModel(Base):
    """智能助手配置管理表"""
    __tablename__ = 'agents'
    id = Column(String(255), primary_key=True, unique=True, nullable=False)
    user_id = Column(String(255), nullable=False)
    agent_name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(Text)
    system_prompt = Column(Text)
    opening_statement = Column(Text)
    knowledge_config = Column(JSON)
    memory_config = Column(JSON)
    websearch_config = Column(JSON)
    mcp_config = Column(JSON)
    model_config = Column(JSON)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)

class TTSConfigModel(Base):
    """TTS配置管理表"""
    __tablename__ = 'tts_configs'
    id = Column(String, primary_key=True, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    user_uuid = Column(String(255), nullable=False)
    description = Column(Text)
    voice_uuid = Column(String(255), unique=True, nullable=False)
    tts_type = Column(Integer)
    charactor = Column(String(255))
    default_emotion = Column(String(255))
    default_language = Column(String(255))
    configs = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)