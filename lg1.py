import os
import json
import requests
from openai import OpenAI
from typing import TypedDict,Annotated
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

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
    
class AgentState(TypedDict):
    messages: Annotated[list, add]

def chatbot(state: AgentState) -> dict:
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=state["messages"],
        tools=TOOLS,
    )
    return {"messages": [response.choices[0].message]}

def tools(state: AgentState) -> dict:
    message = state["messages"][-1]
    results = []
    for call in message.tool_calls:
        if call.function.name == "get_weather":
            args = json.loads(call.function.arguments)
            city = args["city"]
            weather_info = get_weather(city)
            results.append({"role": "tool", "content": f"{city}的天气：{weather_info}", "tool_call_id": call.id})
        if call.function.name == "search_web":
            args = json.loads(call.function.arguments)
            query = args["query"]
            search_results = search_web(query)
            results.append({"role": "tool", "content": f"搜索结果：{search_results}", "tool_call_id": call.id})
    return {"messages": results}

def route(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END



#创建图
graph = StateGraph(AgentState)
#节点
graph.add_node("chatbot", chatbot)
graph.add_node("tools", tools)

#流程
graph.add_edge(START, "chatbot")
graph.add_conditional_edges(
    "chatbot",
      route, {"tools": "tools", END: END})
graph.add_edge("tools", "chatbot")

#使用MemorySaver
checkpointer=MemorySaver()
app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread-1"}}


result1 = app.invoke({"messages": [{"role": "user", "content": "广州天气怎么样"}]},config)

result2 = app.invoke({"messages": [{"role": "user", "content": "那深圳呢"}]},config)
# 最后一条是模型拿着工具结果回的天气
print(result1["messages"][-1].content)
print(result2["messages"][-1].content)
config2 = {"configurable": {"thread_id": "thread-2"}}
result = app.invoke({"messages": [{"role": "user", "content": "帮我搜一下chatgpt的最新消息"}]}, config2)
print(result["messages"][-1].content)
