from models.enums import TransportType, TalkModelType
from typing import (
    Optional,
    List, Dict, Any
)
from pydantic import BaseModel

class CreateLiveAppAPIParameters(BaseModel):
    name: Optional[str]  # 名称
    agent_uuid: Optional[str] = ""  # Agent
    avatar_uuid: Optional[str]  # 数字人 id
    voice_id: Optional[str]  # 音色 id
    transport: Optional[TransportType] = TransportType.RTCPUSH.value  # 推送方式
    talk_model: Optional[TalkModelType] = TalkModelType.WAV2LIPLST.value  # 唇形模型选择
