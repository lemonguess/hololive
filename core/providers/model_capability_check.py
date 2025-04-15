import openai

def check_function_calling(provider) -> bool:
    """Function Calling探测"""
    try:
        # 调用一个需要Function Calling的测试请求
        response = openai.ChatCompletion.create(
            model=provider.value.model_name,
            messages=[{"role": "user", "content": "查询北京天气"}],
            functions=[{
                "name": "get_weather",
                "parameters": {"type": "object", "properties": {"location": {"type": "string"}}}
            }]
        )
        return "function_call" in response.choices[0].message
    except Exception as e:
        print(f"{provider.name}不支持Function Calling: {str(e)}")
        return False

def check_vision_capability(provider) -> bool:
    try:
        # 上传测试图片并请求描述
        response = provider.client.analyze_image(
            image_url="https://example.com/test.jpg",
            query="描述图片内容"
        )
        return len(response.description) > 0
    except NotImplementedError:
        return False