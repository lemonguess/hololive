from sqlalchemy import Column, Integer, String, Text, DateTime as BaseDateTime, JSON, UniqueConstraint, ForeignKey, Table
from datetime import datetime
from models.base import Base
from models.enums import UserRoleType, ModelType, IntEnum
from sqlalchemy.types import TypeDecorator

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
    id = Column(Integer, primary_key=True)
    user_uuid = Column(String(255), unique=True, nullable=False)
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

class BaseSupplierModel(Base):
    """基础供应商管理表"""
    __tablename__ = 'base_suppliers'
    id = Column(Integer, primary_key=True)
    provider_uuid = Column(String(255), unique=True, nullable=False)
    icon = Column(Text)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)


class ModelManagementModel(Base):
    """模型管理表"""
    __tablename__ = 'imodel_management'
    id = Column(Integer, primary_key=True)
    user_provider_uuid = Column(String(255), nullable=False)  # 外键到 user_suppliers.user_provider_uuid
    user_uuid = Column(String(255), nullable=False)
    imodel_uuid = Column(String(255), unique=True, nullable=False)  # 模型唯一标识
    imodel_type = Column(IntEnum(ModelType), nullable=False)  # 模型类型，使用枚举类 ModelType
    name = Column(String(255), nullable=False)  # 模型名称
    description = Column(Text)
    icon = Column(Text)
    config = Column(JSON)  # 模型配置，JSON类型
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    create_time = Column(DateTime, default=datetime.utcnow)  # 创建时间





class UserSupplierModel(Base):
    """用户供应商管理表"""
    __tablename__ = 'user_suppliers'
    id = Column(Integer, primary_key=True)
    user_uuid = Column(String(255), nullable=False)  # 确保该值在 users 表中存在
    provider_uuid = Column(String(255), nullable=False)  # 确保该值在 base_suppliers 表中存在
    user_provider_uuid = Column(String(255), unique=True, nullable=False)  # 确保该值是唯一的
    api_key = Column(Text, nullable=False)
    base_url = Column(Text, nullable=False)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        UniqueConstraint('user_uuid', 'provider_uuid', name='uq_user_provider'),  # 确保 user_uuid 和 provider_uuid 的组合是唯一的
    )

class AgentConfigModel(Base):
    """智能助手配置管理表"""
    __tablename__ = 'agent_configs'
    id = Column(Integer, primary_key=True)
    agent_uuid = Column(String(255), unique=True, nullable=False)
    llm_uuid = Column(String(255), nullable=False)  # 外键到llms.llm_uuid
    user_uuid = Column(String(255), nullable=False)
    agent_name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(Text)
    system_prompt = Column(Text)
    opening_statement = Column(Text)
    knowledge_config = Column(JSON)
    memory_config = Column(JSON)
    websearch_config = Column(JSON)
    mcp_config = Column(JSON)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)

class TTSConfigModel(Base):
    """TTS配置管理表"""
    __tablename__ = 'tts_configs'
    id = Column(Integer, primary_key=True)
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