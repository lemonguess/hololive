import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import random


def bing_search(query, max_results=5):
    # 构造搜索URL并发送请求
    url = f"https://cn.bing.com/search?q={quote_plus(query)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 解析搜索结果
        results = []
        for item in soup.select('ol#b_results li.b_algo'):
            title = item.find('h2').get_text(strip=True) if item.find('h2') else '无标题'
            href = item.find('a')['href'] if item.find('a') else '#'
            snippet = item.find('p').get_text(strip=True) if item.find('p') else '无摘要'

            results.append({'title': title, 'href': href, 'body': snippet})
            if len(results) >= max_results:
                break

        # 反爬延迟
        time.sleep(random.uniform(1, 3))
        return results

    except Exception as e:
        print(f"Bing搜索失败: {str(e)}")
        return []
    