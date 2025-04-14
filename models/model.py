from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from models.base import Base
from models.enums import IntEnum, UserRoleType


class BaseSupplierModel(Base):
    """基础供应商管理表"""
    __tablename__ = 'base_suppliers'
    id = Column(Integer, primary_key=True)
    provider_uuid = Column(String(255), unique=True, nullable=False)
    icon = Column(Text)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)

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


class UserSupplierModel(Base):
    """用户供应商管理表"""
    __tablename__ = 'user_suppliers'
    id = Column(Integer, primary_key=True)
    user_uuid = Column(String(255), nullable=False)
    provider_uuid = Column(String(255), nullable=False)  # 外键到suppliers.provider_uuid
    user_provider_uuid = Column(String(255), unique=True, nullable=False)
    api_key = Column(Text, nullable=False)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)

class LLMModel(Base):
    """LLM模型管理表"""
    __tablename__ = 'llms'
    id = Column(Integer, primary_key=True)
    llm_uuid = Column(String(255), unique=True, nullable=False)
    user_provider_uuid = Column(String(255), nullable=False)  # 外键到user_suppliers.user_provider_uuid
    user_uuid = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    max_tokens = Column(Integer)
    context_length = Column(Integer)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    create_time = Column(DateTime, default=datetime.utcnow)

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