from enum import Enum

class TransportType(Enum):
    """推送方式"""
    RTMP = 0
    WEBRTC = 1
    RTCPUSH = 2

class TalkModelType(Enum):
    """lips模型类别"""
    WAV2LIP = 0
    WAV2LIPLST = 1
    MUSETALK = 2

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
