import json

CITIES = ["广州", "湛江", "深圳","东莞"]

# 这是一个假模型：不用 Key、不用联网。
# 它假装自己是大模型，按规则返回一段 JSON 字符串。
def fake_llm(messages):
    last = messages[-1]
    # 如果最后一条是工具返回的结果，说明上一轮查到的天气已经回来了。
    # 先看这一问里提了几个城市、已经查了几个：没查完就继续查，查齐了才拼最终答案。
    if last["role"] == "tool":
        # 从后往前翻：翻到用户那句话就停，中间的工具结果就是这一问查到的。
        user_text = ""
        tool_msgs = []
        for m in reversed(messages):
            if m["role"] == "user":
                user_text = m["content"]
                break
            if m["role"] == "tool":
                tool_msgs.append(m)
        tool_msgs.reverse()
        city_count = 0
        for c in CITIES:
            if c in user_text:
                city_count += 1
        if len(tool_msgs) < city_count:
            return json.dumps({"answer": "继续查下一个城市。", "topic": "weather"}, ensure_ascii=False)
        parts = []
        for m in tool_msgs:
            parts.append(m["content"])
        return json.dumps({"answer": " ".join(parts), "topic": "final"}, ensure_ascii=False)
    user_text = last["content"]
    if "天气" in user_text:
        data = {"answer": "我还不会查这个城市的天气，但收到了你的问题。", "topic": "weather"}
    elif "你好" in user_text:
        data = {"answer": "你好，我是你的第一个 Agent 原型。", "topic": "greeting"}
    else:
        data = {"answer": f"你刚说的是：{user_text}", "topic": "echo"}
    return json.dumps(data, ensure_ascii=False)


def get_weather(city):
    print("工具被调用了")
    if city == "广州":
        return {"city": "广州", "weather": "晴", "temp": "26°C"}
    elif city == "湛江":
        return {"city": "湛江", "weather": "多云", "temp": "28°C"}
    elif city == "深圳":
        return {"city": "深圳", "weather": "阴", "temp": "27°C"}
    elif city == "东莞":
        return{"city":"东莞","weather":"小雨","temp":"25°C"}
    else:
        return {"city": city, "weather": "未知", "temp": "未知"}


def parse_json_response(text):
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)
    if "answer" not in data:
        raise ValueError("返回里缺少 answer")
    return data


def chat_loop(history, user_text, max_steps=5):
    history.append({"role": "user", "content": user_text})
    queried = []
    for step in range(max_steps):
        raw = fake_llm(history)
        try:
            result = parse_json_response(raw)
        except Exception:
            raw = fake_llm(history)
            result = parse_json_response(raw)
        print(f"第 {step + 1} 轮：topic={result['topic']}")

        if result["topic"] == "weather":
            # 找出问题里提到的、还没查过的城市
            todo = []
            for c in CITIES:
                if c in user_text and c not in queried:
                    todo.append(c)
            if not todo:
                history.append({"role": "assistant", "content": result["answer"]})
                return result
            city = todo[0]
            info = get_weather(city)
            queried.append(city)
            history.append({"role": "tool", "content": f"{info['city']}今天的天气是{info['weather']}，温度是{info['temp']}。"})
            continue
        history.append({"role": "assistant", "content": result["answer"]})
        return result
    return {"answer": "步数用完了", "topic": "timeout"}


def main():
    history = [
        {"role": "system", "content": "你是一个助手，必须只返回 JSON。"}
    ]
    print("输入 quit 退出")
    while True:
        user_text = input("你: ").strip()
        if user_text.lower() == "quit":
            break
        result = chat_loop(history, user_text)
        print("Agent:", result)


if __name__ == "__main__":
    main()
