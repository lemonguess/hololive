from enum import Enum
from sqlalchemy import TypeDecorator, Integer

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

class TransportType(Enum):
    """推送方式"""
    RTMP = 0
    WEBRTC = 1
    RTCPUSH = 2

    def determine_existence_type(self, input_val):
        """
        判断输入值是枚举的 name 还是 value
        :param input_val: 可以是字符串（name）或整数（value）
        :return: 'name'、'value' 或 None
        """
        # 检测是否为 name
        if isinstance(input_val, str):
            if input_val in self.__class__.__members__:
                return 'name'

        # 检测是否为 value
        elif isinstance(input_val, int):
            all_values = {member.value for member in self.__class__}
            if input_val in all_values:
                return 'value'

        # 无匹配项
        return None

class TalkModelType(Enum):
    """lips模型类别"""
    WAV2LIP = 0
    WAV2LIPLST = 1
    MUSETALK = 2

class UserRoleType(Enum):
    """用户权限角色"""
    ADMIN = 0  # 管理员
    USER = 1  # 普通账号
    TEST = 2  # 测试账号
    FORBID = 3  # 禁用账号

class TTSType(Enum):
    """TTS类型"""
    GPTSOVITS = 0
    XTTS = 1
    COSYVOICE = 2
    EDGETTS = 3

class ASRType(Enum):
    """ASR类型"""
    FUNASR = 0
    TENCENTASR = 1

class LLMProvider(Enum):
    """大语言模型供应商枚举类"""
    OPENAI = 1  # OpenAI
    ANTHROPIC = 2  # Anthropic
    AZURE_OPENAI = 3  # Azure OpenAI
    GEMINI = 4  # Google Gemini
    GOOGLE_CLOUD = 5  # Google Cloud
    NVIDIA_API = 6  # Nvidia API Catalog
    NVIDIA_NIM = 7  # Nvidia NIM
    NVIDIA_TRITON = 8  # Nvidia Triton Inference Server
    AWS_BEDROCK = 9  # AWS Bedrock
    OPENROUTER = 10  # OpenRouter
    COHERE = 11  # Cohere
    TOGETHER_AI = 12  # together.ai
    OLLAMA = 13  # Ollama
    MISTRAL_AI = 14  # Mistral AI
    GROQ = 15  # groqcloud
    REPLICATE = 16  # Replicate
    HUGGING_FACE = 17  # Hugging Face
    XORBITS = 18  # Xorbits inference
    ZHIPU = 19  # 智谱AI
    BAICHUAN = 20  # 百川智能
    XUNFEI = 21  # 讯飞星火
    MINIMAX = 22  # Minimax
    TONGYI = 23  # 通义千问
    ERNIE = 24  # 文心一言
    MOONSHOT = 25  # 月之暗面
    TENCENT = 26  # 腾讯云
    STEPFUN = 27  # 阶跃星辰
    VOLCANO = 28  # 火山引擎
    YI = 29  # 零一万物
    QIHU_360 = 30  # 360智脑
    AZURE_AI = 31  # Azure AI Studio
    DEEPSEEK = 32  # DeepSeek
    TENCENT_HUNYUAN = 33  # 腾讯混元
    SILICONFLOW = 34  # SILICONFLOW
    JINA_AI = 35  # Jina AI
    CHATGLM = 36  # ChatGLM
    XINFERENCE = 37  # Xinference
    OPENLLM = 38  # OpenLLM
    LOCALAI = 39  # LocalAI
    OPENAI_COMPATIBLE = 40  # OpenAI API-Compatible
    PERFX = 41  # PerfXCloud
    LEPTON = 42  # Lepton AI
    NOVITA = 43  # novita.ai
    SAGEMAKER = 44  # Amazon Sagemaker
    TEI = 45  # Text Embedding Inference
    GPU_STACK = 46  # GPUStack
