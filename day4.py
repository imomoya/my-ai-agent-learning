import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
MAX_SPEND_USD = 0.10
total_cost = 0.0

TOOLS = [
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
            args = json.loads(call.function.arguments)
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
        result = chat_loop(history, user_text)
        print("Agent:", result)


if __name__ == "__main__":
    main()
