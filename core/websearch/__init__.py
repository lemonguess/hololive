from core.websearch.bing_search import bing_search
from core.websearch.baidu_search import baidu_search
from core.websearch.bocha_seach import bocha_search


def web_search(query, engine='bing', max_results=5):
    """
    参数说明：
    - engine : 'bing' 或 'baidu'
    - max_results : 最大返回结果数（默认5）
    """
    if engine == 'bing':
        data = bing_search(query, max_results=max_results)
    elif engine == 'baidu':
        data = baidu_search(query, max_results=max_results)
    elif engine == 'bocha':
        data = bocha_search(query, max_results=max_results)
    else:
        raise ValueError("不支持该搜索引擎")
    return data
    # # 转换为字符串格式
    # return "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in data])
if __name__ == '__main__':
    # 调用Bing搜索
    print(web_search("李小龍", engine='bocha', max_results=5))

    # 调用百度搜索
    # print(web_search("李小龍", engine='baidu'))