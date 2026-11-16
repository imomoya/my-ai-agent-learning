import json

# 这是一个假模型：不用 Key、不用联网。
# 它假装自己是大模型，按规则返回一段 JSON 字符串。
def fake_llm(messages):
    user_text = messages[-1]["content"]
    if "天气" in user_text:
        data = {"answer": "我还不会查天气，但我收到了你的问题。", "topic": "weather"}
    elif "你好" in user_text:
        data = {"answer": "你好，我是你的第一个 Agent 原型。", "topic": "greeting"}
    else:
        data = {"answer": f"你刚说的是：{user_text}", "topic": "echo"}
    return json.dumps(data, ensure_ascii=False)


def parse_json_response(text):
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)
    if "answer" not in data:
        raise ValueError("返回里缺少 answer")
    return data


def chat_once(history, user_text):
    history.append({"role": "user", "content": user_text})
    raw = fake_llm(history)
    try:
        result = parse_json_response(raw)
    except Exception:
        raw = fake_llm(history)
        result = parse_json_response(raw)
    history.append({"role": "assistant", "content": result["answer"]})
    return result


def main():
    history = [
        {"role": "system", "content": "你是一个助手，必须只返回 JSON。"}
    ]
    print("输入 quit 退出")
    while True:
        user_text = input("你: ").strip()
        if user_text.lower() == "quit":
            break
        result = chat_once(history, user_text)
        print("Agent:", result)


if __name__ == "__main__":
    main()