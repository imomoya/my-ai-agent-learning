# my-ai-agent-learning

手写 AI Agent 的学习记录：从假模型开始，一步一步写到接真实 API，再用 LangGraph 把循环重建一遍。

## 进度

- **Day 1：`day1.py`** — 假模型 + JSON 对话。`fake_llm` 按规则返回 JSON，`parse_json_response` 校验，`chat_once` 跑一轮对话。
- **Day 2：`day2.py`** — 第一次真正调用工具。模型只返回 topic，程序按 topic 调 `get_weather`，再把结果拼进回答。
- **Day 3：`day3.py`** — 循环。`chat_loop` 最多 5 轮，工具结果以 tool 消息写回 history，一问可以查多个城市。
- **Day 4：`day4.py`** — 接真实 DeepSeek API。模型自己决定调哪个工具（function calling），工具结果以含 tool_call_id 的 tool 消息喂回；带每轮 tokens/花费日志和累计花费上限、工具白名单（`ALLOWED_TOOLS`，名单外的工具会被拦住并把错误喂回模型），还有真联网搜索工具 `search_web`（DeepSeek Search API），模型自己决定什么时候搜；还有记忆裁剪（`trim_history`，只留 system + 最近 2 问，history 不再无限变长）。
- **LangGraph：`lg1.py`** — 用 LangGraph 重建 Day 4 的循环：StateGraph + chatbot 节点 + tools 节点 + 条件边（`route`），查天气和联网搜索两条线都跑通；配 `MemorySaver` + `thread_id`，多轮对话记得上文。

## 运行

Day 1–3 不用 Key、不用联网，直接跑：

```bash
python day1.py
```

Day 4 需要装 SDK 并设置 Key（Key 只放环境变量，不要写进代码）：

```bash
pip install openai requests
```

```powershell
$env:DEEPSEEK_API_KEY="你的 Key"
python day4.py
```

`lg1.py` 同样需要 Key，另外要装 LangGraph：

```bash
pip install langgraph
```

```powershell
$env:DEEPSEEK_API_KEY="你的 Key"
python lg1.py
```

## 说明

学习项目，不是生产代码。`get_weather` 返回的是写死的假数据，不是真实天气；重点是 Agent 循环、工具调用和上下文管理这些机制本身。`TOOLS` 里的 `delete_file` 是白名单演示用的诱饵，只有说明书、没有实现，调用会被白名单拦住。`search_web` 是真的联网搜索，每次成功搜索另外计费，不走 tokens 花费统计。`lg1.py` 里的 `get_weather` 同样是假数据；`MemorySaver` 只存内存，关掉程序对话记录就没了。
