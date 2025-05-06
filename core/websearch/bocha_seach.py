import requests
import json


def bocha_search(query: str, api_key: str=None, mode: str = "web", max_results: int = 5) -> str:
    """
    调用博查API进行搜索
    :param query: 搜索关键词
    :param api_key: API密钥（格式为`sk-xxxxxx`）
    :param mode: 搜索模式，可选 `web`（网页搜索）或 `ai`（多模态搜索）
    :param max_results: 最大返回结果数（1-50）
    :return: 格式化后的搜索结果字符串
    """
    # 配置API端点
    url = "https://api.bochaai.com/v1/web-search" if mode == "web" else "https://api.bochaai.com/v1/ai-search"
    api_key = "sk-9a538f2c30534de1b20895782d39a987"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "count": max_results,
        "freshness": "noLimit",
        "answer": False,  # AI模式是否启用大模型总结
        "stream": False  # 是否启用流式输出
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # 检查HTTP错误
        data = response.json()

        # 解析多模态结果
        if mode == "ai":
            return _parse_ai_results(data)
        else:
            return _parse_web_results(data)

    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"
    except KeyError:
        return "响应格式解析错误"


def _parse_web_results(data: dict) -> str:
    """解析普通网页搜索结果"""
    results = data.get("data", {}).get("webPages", {}).get("value", [])
    return [{"title": r["name"], "href": r["url"], "body": r["snippet"]} for r in results]
    # return "\n\n".join([
    #     f"Title: {item['name']}\nURL: {item['url']}\nSnippet: {item['snippet']}"
    #     for item in results[:5]
    # ])


def _parse_ai_results(data: dict) -> str:
    """解析AI多模态结果（天气/百科/医疗等卡片）"""
    output = []
    # 提取文字结果
    web_pages = data.get("data", {}).get("webPages", {}).get("value", [])
    for item in web_pages[:3]:
        output.append(f"📝 文字结果:\n标题: {item['name']}\n链接: {item['url']}\n摘要: {item['snippet']}")

    # 提取垂直卡片（如天气/百科）
    content_type = data.get("data", {}).get("content_type", "")
    if content_type == "weather":
        weather_info = data["data"]["weatherCard"]
        output.append(
            f"🌤️ 天气卡片:\n城市: {weather_info['city']}\n温度: {weather_info['temp']}℃\n天气: {weather_info['condition']}")

    return "\n\n".join(output)