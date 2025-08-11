import os
from dotenv import load_dotenv
import requests

# 配置参数
load_dotenv()
API_KEY = os.getenv("SERPAPI_KEY")  # 从环境变量读取API密钥
SEARCH_ENGINE = "google"  # 可改为"bing"、"yahoo"等


def serpapi_search(query: str, num_results: int = 5) -> list[dict]:
    """
    执行SerpAPI搜索并返回结构化结果
    :param query: 搜索关键词
    :param num_results: 需要返回的结果数量
    :return: 结构化结果列表
    """
    if not API_KEY:
        raise ValueError("未设置SERPAPI_KEY环境变量。请在.env文件中设置您的API密钥。")
        
    try:
        # 构造API请求参数
        params = {
            "engine": SEARCH_ENGINE,
            "q": query,
            "api_key": API_KEY,
            "num": num_results,  # 控制返回结果数量
            "hl": "zh-CN",         # 语言设置（中文可设为"zh-CN"）
            "gl": "cn"          # 国家/地区代码
        }

        # 发送API请求
        response = requests.get(
            "https://serpapi.com/search",
            params=params,
            timeout=15
        )
        response.raise_for_status()  # 检查HTTP错误

        # 解析结果
        search_data = response.json()
        return _parse_serpapi_results(search_data)

    except Exception as e:
        print(f"搜索失败: {str(e)}")
        return []

def _parse_serpapi_results(data: dict) -> list[dict]:
    """解析SerpAPI返回的原始数据"""
    results = []
    
    # 提取有机搜索结果（非广告）
    if "organic_results" in data:
        for item in data["organic_results"]:
            result = {
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet"),
                "source": "web",
                "timestamp": item.get("date")  # 部分结果有时间戳
            }
            results.append(result)
    
    # 可选：提取知识图谱信息（如直接答案）
    if "knowledge_graph" in data:
        kg = data["knowledge_graph"]
        results.insert(0, {  # 将知识图谱结果置顶
            "title": kg.get("title"),
            "url": kg.get("source")["link"] if "source" in kg else "",
            "snippet": kg.get("description"),
            "source": "knowledge_graph"
        })
    
    return results

# 使用示例
if __name__ == "__main__":
    test_query = "deepseek-R1模型使用了什么新的训练方法？"
    search_results = serpapi_search(test_query)
    
    # 打印结果
    print(f"搜索词: {test_query}")
    for idx, result in enumerate(search_results, 1):
        print(f"\n结果 {idx}:")
        print(f"标题: {result['title']}")
        print(f"链接: {result['url']}")
        print(f"摘要: {result['snippet']}")