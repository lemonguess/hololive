from langchain_openai.chat_models.base import BaseChatOpenAI

tavily_api_key="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"
# 初始化LLM
llm = BaseChatOpenAI(
    model='deepseek-chat',  # 使用DeepSeek聊天模型
    openai_api_key='sk-2433c906e5a343ca9de7b56c45888f99',
    openai_api_base='https://api.deepseek.com',
    max_tokens=64*1024  # 设置最大生成token数
)
def get_llm(*args, **kwargs):
    return llm