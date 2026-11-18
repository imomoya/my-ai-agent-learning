import os
import json
import requests
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
MAX_SPEND_USD = 0.10
total_cost = 0.0

ALLOWED_TOOLS = ["get_weather", "search_web"]
TOOLS =[
    { "type": "function",
        "function": {
            "name": "search_web",
            "description": "在网页上搜索信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "删除一个文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "要删除的文件名"}
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询一个城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，比如深圳"}
                },
                "required": ["city"],
            },
        },
    }
]

def search_web(query):
    print("搜索被调用了：", query)
    key = os.environ.get("DEEPSEEK_API_KEY")
    response = requests.post(
        "https://api.deepseek.com/v1/tools/search",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "count": 3,
        },
    )
    response.raise_for_status()
    lines = []
    for result in response.json()["results"]:
        lines.append(f"{result['title']}：{result['snippet']}（{result['url']}）")
    return "\n".join(lines)

def get_weather(city):
    if city == "广州":
        return {"city": "广州", "weather": "晴", "temp": "26°C"}
    elif city == "湛江":
        return {"city": "湛江", "weather": "多云", "temp": "28°C"}
    elif city == "深圳":
        return {"city": "深圳", "weather": "阴", "temp": "27°C"}
    elif city == "东莞":
        return {"city": "东莞", "weather": "小雨", "temp": "25°C"}
    else:
        return {"city": city, "weather": "未知", "temp": "未知"}
    
def trim_history(history, keep_turns):
    positions = []
    for i, m in enumerate(history):
        if isinstance(m, dict):
            role = m["role"]
        else:
            role = m.role
        if role == "user":
            positions.append(i)
    if len(positions) <= keep_turns:
        return history
    cut = positions[-keep_turns]
    new_history = history[:1] + history[cut:]
    print(f"裁剪前 {len(history)} 条，裁剪后 {len(new_history)} 条")
    return new_history



def chat_loop(history, user_text, max_steps=5):
    global total_cost
    history.append({"role": "user", "content": user_text})
    for step in range(max_steps):
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=history,
            tools=TOOLS,
        )
        cost =response.usage.prompt_tokens*0.15 / 1000000+response.usage.completion_tokens*0.60 / 1000000
        total_cost+=cost
        message = response.choices[0].message
        print(f"第 {step + 1} 轮：tool_calls={bool(message.tool_calls)}")
        print(f"本轮：输入 {response.usage.prompt_tokens} tokens，输出 {response.usage.completion_tokens} tokens，花费 ${cost:.6f}，累计花费 ${total_cost:.6f}")
        if total_cost > MAX_SPEND_USD:
                    return "已达到最大消费额度"
        if not message.tool_calls:
            history.append({"role": "assistant", "content": message.content})
            return message.content
        history.append(message)
        for call in message.tool_calls:
            if call.function.name not in ALLOWED_TOOLS:
                history.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": f"工具 {call.function.name} 不在白名单中，不允许调用。"
                })
                print(f"工具 {call.function.name} 被白名单拦住了")
                continue
            args = json.loads(call.function.arguments)
            if call.function.name == "search_web":
                info = search_web(args["query"])
                print("工具被调用了：", args["query"])
                history.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": info,
                })
            elif call.function.name == "get_weather":
                info = get_weather(args["city"])
                print("工具被调用了：", args["city"])
                history.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": f"{info['city']}今天的天气是{info['weather']}，温度是{info['temp']}。",
            })
        
    return "步数用完了"


def main():
    history = [{"role": "system", "content": "你是一个助手。"}]
    print("输入 quit 退出")
    while True:
        user_text = input("你: ").strip()
        if user_text.lower() == "quit":
            break
        history = trim_history(history, 2)
        result = chat_loop(history, user_text)
        print("Agent:", result)
        print(history)


if __name__ == "__main__":
    main()

