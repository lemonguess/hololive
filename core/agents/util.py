from core.llms.get_instance import get_chat_instance
from core.websearch import web_search
from models.enums import LLMProvider
from models.fields import LLMConf
# from duckduckgo_search import DDGS


def call_llm(prompt):
    key = "sk-cnyrmjcocozwaiizfxyzjulxtobfgwzbjgpevaoacnqtdvaf"
    model_name = "Qwen/Qwen2.5-7B-Instruct"
    mdl = get_chat_instance(LLMProvider.SILICONFLOW, LLMConf(api_key=key, model_name=model_name))
    res, tokens = mdl.chat(system="You are a helpful assistant.",history=[{"role": "user", "content": prompt}],
                                                               gen_conf={"temperature": 0.7, "max_tokens": 1000})
    return res


def search_web(query):
    # results = DDGS().text(query, max_results=5)
    results = web_search(query, engine='bing', max_results=5)
    # Convert results to a string
    results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
    return results_str


if __name__ == "__main__":
    print("## Testing call_llm")
    prompt = "In a few words, what is the meaning of life?"
    print(f"## Prompt: {prompt}")
    response = call_llm(prompt)
    print(f"## Response: {response}")

    print("## Testing search_web")
    query = "Who won the Nobel Prize in Physics 2024?"
    print(f"## Query: {query}")
    results = search_web(query)
    print(f"## Results: {results}")