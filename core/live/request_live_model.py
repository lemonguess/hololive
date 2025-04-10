from enum import Enum
from typing import (
    Optional,
    List, Dict, Any
)
from typing import Literal
from pydantic import BaseModel
class TransportType(Enum):
    RTMP = "rtmp"
    WEBRTC = "webrtc"
    RTCPUSH = "rtcpush"

class CreateLiveAppAPIParameters(BaseModel):
    name: Optional[str]  # 名称
    agent_uuid: Optional[str] = ""  # Agent
    avatar_uuid: Optional[str]  # 数字人 id
    voice_id: Optional[str]  # 音色 id
    transport: Optional[TransportType] = TransportType.RTCPUSH  # 推送方式
