from openai import OpenAI
from models.fields import LLMConf, EmbeddingConf, OpenaiClientConf
import os
import numpy as np


def get_llm_client(openai_client: OpenaiClientConf)->OpenAI:
    _client = OpenAI(api_key=openai_client.api_key, base_url=openai_client.api_base)
    return _client

def _call_llm(_client: OpenAI, llm_config: LLMConf):
    _response = _client.chat.completions.create(
        model=llm_config.model_name,
        messages=llm_config.messages,
        temperature=llm_config.temperature
    )
    return _response.choices[0].message.content
def call_llm(messages):
    _client = get_llm_client(OpenaiClientConf(api_key="sk-cnyrmjcocozwaiizfxyzjulxtobfgwzbjgpevaoacnqtdvaf",
                                             api_base="https://api.siliconflow.cn"))
    _response = _client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=messages
    )
    return _response.choices[0].message.content


def get_embedding(_client: OpenAI, embedding_config: EmbeddingConf):
    _response = _client.embeddings.create(
        model=embedding_config.model_name,
        input=embedding_config.text
    )

    # Extract the embedding vector from the response
    _embedding = _response.data[0].embedding

    # Convert to numpy array for consistency with other embedding functions
    return np.array(_embedding, dtype=np.float32)


if __name__ == "__main__":
    client = get_llm_client(OpenaiClientConf(api_key="sk-cnyrmjcocozwaiizfxyzjulxtobfgwzbjgpevaoacnqtdvaf", api_base="https://api.siliconflow.cn"))
    # Test the LLM call
    messages = [{"role": "user", "content": "In a few words, what's the meaning of life?"}]
    response = call_llm(client, LLMConf(messages=messages, model_name="Qwen/Qwen2.5-7B-Instruct", temperature=0.7))
    print(f"Prompt: {messages[0]['content']}")
    print(f"Response: {response}")
    # Test the embedding call
    # text = "This is a test sentence."
    # embedding = get_embedding(client, EmbeddingConf(text=text, model_name="BAAI/bge-large-zh-v1.5"))
    # print(f"Embedding for '{text}': {embedding}")
