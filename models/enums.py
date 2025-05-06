from enum import Enum

class ModelType(Enum):
    """模型类型枚举类"""
    # TEXT = 1  # 文本模型
    # IMAGE = 2  # 图像模型
    # MULTIMODAL = 3  # 多模态模型
    # TTS = 4  # TTS模型
    # ASR = 5  # ASR模型
    CHAT = 'chat'
    EMBEDDING = 'embedding'
    SPEECH2TEXT = 'speech2text'
    IMAGE2TEXT = 'image2text'
    RERANK = 'rerank'
    TTS = 'tts'

class LLMType(Enum):
    CHAT = 'chat'
    EMBEDDING = 'embedding'
    SPEECH2TEXT = 'speech2text'
    IMAGE2TEXT = 'image2text'
    RERANK = 'rerank'
    TTS = 'tts'


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
    OPENAI = "OpenAI"
    AZURE_OPENAI = "Azure-OpenAI"
    ZHIPU_AI = "ZHIPU-AI"
    TONGYI_QIANWEN = "Tongyi-Qianwen"
    OLLAMA = "Ollama"
    LOCALAI = "LocalAI"
    XINFERENCE = "Xinference"
    MOONSHOT = "Moonshot"
    DEEPSEEK = "DeepSeek"
    VOLC_ENGINE = "VolcEngine"
    BAICHUAN = "BaiChuan"
    MINIMAX = "MiniMax"
    MISTRAL = "Mistral"
    GEMINI = "Gemini"
    BEDROCK = "Bedrock"
    GROQ = "Groq"
    OPENROUTER = "OpenRouter"
    STEP_FUN = "StepFun"
    NVIDIA = "NVIDIA"
    LM_STUDIO = "LM-Studio"
    OPENAI_API_COMPATIBLE = "OpenAI-API-Compatible"
    VLLM = "VLLM"
    COHERE = "Cohere"
    LEPTON_AI = "LeptonAI"
    TOGETHER_AI = "TogetherAI"
    PERFX_CLOUD = "PerfXCloud"
    UPSTAGE = "Upstage"
    NOVITA_AI = "novita.ai"
    SILICONFLOW = "SILICONFLOW"
    PPIO = "PPIO"
    YI_01_AI = "01.AI"
    REPLICATE = "Replicate"
    TENCENT_HUNYUAN = "Tencent Hunyuan"
    XUNFEI_SPARK = "XunFei Spark"
    BAIDU_YIYAN = "BaiduYiyan"
    ANTHROPIC = "Anthropic"
    GOOGLE_CLOUD = "Google Cloud"
    HUGGING_FACE = "HuggingFace"
    GPUSTACK = "GPUStack"
    MODEL_SCOPE = "ModelScope"

class Bucket(Enum):
    public_bucket = "ai-public-bucket"
    private_bucket = "ai-private-bucket"