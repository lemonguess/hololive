from rag.llm import ChatModel
from models.enums import LLMProvider
from models.fields import LLMConf

def get_chat_instance(factory:LLMProvider, llm_conf: LLMConf):
    """
    根据传入的 LLMProvider 枚举值返回相应的类对象。
    Args:
        provider (LLMProvider): LLM 提供者枚举值。
    Returns:
        Base: 返回对应的类对象。
    Raises:
        ValueError: 如果传入的 provider 不被支持，则抛出异常。
    """
    assert factory.value in ChatModel, f"Chat model from {factory.value} is not supported yet."
    mdl = ChatModel[factory.value](
        llm_conf.api_key, llm_conf.model_name, base_url=llm_conf.base_url)
    return mdl
if __name__ == '__main__':
    key = "sk-cnyrmjcocozwaiizfxyzjulxtobfgwzbjgpevaoacnqtdvaf"
    model_name = "Qwen/Qwen2.5-7B-Instruct"
    mdl = get_chat_instance(LLMProvider.SILICONFLOW, LLMConf(api_key=key, model_name=model_name))
    print(mdl.chat(system="You are a helpful assistant.",history=[{"role": "user", "content": "你是鸡巴谁啊!"}],
                                                               gen_conf={"temperature": 0.7, "max_tokens": 1000}))
