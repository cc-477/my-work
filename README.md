# 从零开始的 AI 应用与数据练习

河南财政金融学院 · 数字经济专业 · 大三（2028 届）

这个仓库记录我从零学 Python、SQL、大模型应用的练习过程。**它不是项目作品集，是过程记录**——包括我卡在哪儿、错在哪儿、怎么绕过去的。

## 目录

| 路径 | 是什么 |
|---|---|
| `chat.py` | 调用大模型 API 的命令行对话脚本。手写 .env 解析、token 统计、错误兜底，支持开关思考模式 |
| `prompt.txt` | 对话用的 system 提示词。改这个文件就能换模型身份，不用动代码 |
| `sql_practice.py` | 本地 SQL 练习器。用 sqlite3 建了两张表（郑州真实 AI/数据岗），5 道题自动判对错 |
| `sql/week1.sql` | 我写的第一周 SQL 答案 |
| `badcase.md` | 大模型错误记录表。把模型答错的地方逐条记下来，按错误类型分类，作为后续做 RAG 评测的基础 |

## 怎么跑

需要 Python 3.10。

```bash
python -m venv .venv
.venv\Scripts\activate
pip install openai
```

复制 `.env.example` 为 `.env`，填入自己的 `DEEPSEEK_API_KEY`，然后：

```bash
python chat.py
python sql_practice.py
```

## 进度

**第 1 周（2026.11.25 – 11.29）**
- 环境搭好：Python 3.10 虚拟环境 + pandas / matplotlib / openai / streamlit
- 接通 DeepSeek API，跑通第一个对话脚本，对比了快速模式与思考模式的 token 消耗（同一道算术题：61 vs 145）
- 做完 SQL 入门 5 题：SELECT、WHERE、ORDER BY、LIMIT、GROUP BY、JOIN
- 记录第一批大模型 badcase：发现它会把真实的政策文件名配上编造的文号

## 下一步

寒假做一个「河南省数字经济政策助手」：把省内政策文件做成知识库，用 RAG 让模型基于原文回答，并用 badcase.md 里的记录做评测，看准确率能提到多少。

## 说明

仓库内不含任何密钥。API Key 存在本地 `.env`，已被 `.gitignore` 排除。
