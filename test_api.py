# -*- coding: utf-8 -*-
"""
接口连通性测试
用法：  python test_api.py
作用：  不进入对话，只发一次请求，确认 Key、余额、模型名三件事都对。
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from openai import OpenAI

MODEL = "deepseek-flash"
BASE_URL = "https://api.deepseek.com"


def load_key():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print("[X] 找不到 .env 文件")
        print("    做法：把 .env.example 复制一份改名为 .env，填入 Key")
        return None

    with open(env_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "DEEPSEEK_API_KEY":
                v = v.strip().strip('"').strip("'")
                if not v or "你的密钥" in v:
                    print("[X] .env 里 Key 还是占位符，请换成你自己的")
                    return None
                return v
    print("[X] .env 里没有 DEEPSEEK_API_KEY 这一行")
    return None


def main():
    print("=" * 56)
    print("  API 连通性测试")
    print("=" * 56)
    print()

    key = load_key()
    if not key:
        sys.exit(1)

    # 只显示前 6 位，确认读到了对的 key，但不泄露全文
    print("读取到 Key :", key[:6] + "..." + key[-4:] if len(key) > 12 else "(长度异常)")
    print("Key 长度   :", len(key), "(正常应为 30-60 位)")
    print("接口地址   :", BASE_URL)
    print("模型名     :", MODEL)
    print()
    print("正在发送请求 ...")
    print()

    client = OpenAI(api_key=key, base_url=BASE_URL, timeout=60)

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "回答简短，不超过30字。"},
                {"role": "user", "content": "用一句话说明你是哪个模型。"},
            ],
            temperature=0,
            max_tokens=200,
            extra_body={"thinking": {"type": "disabled"}},  # 关掉思考，否则正文可能被推理挤掉
        )
    except Exception as e:
        msg = str(e)
        print("[X] 失败")
        print("    原文：", msg)
        print()
        if "401" in msg or "auth" in msg.lower() or "invalid" in msg.lower():
            print("    诊断：密钥无效。可能复制时漏了字符、多了空格，或已被删除。")
            print("    处理：回 platform.deepseek.com 重新创建一把")
        elif "402" in msg or "insufficient" in msg.lower() or "balance" in msg.lower():
            print("    诊断：余额不足。")
            print("    处理：platform.deepseek.com -> 充值 -> 在线充值，最低 10 元")
        elif "404" in msg or ("model" in msg.lower() and "not" in msg.lower()):
            print("    诊断：模型名不存在。")
            print("    处理：当前应为 deepseek-flash")
        elif "connect" in msg.lower() or "timeout" in msg.lower() or "ssl" in msg.lower():
            print("    诊断：网络连不上。")
            print("    处理：检查是否开了代理，或换个网络再试")
        else:
            print("    诊断：未归类错误，把上面原文发给 AI 判断")
        sys.exit(1)

    answer = (resp.choices[0].message.content or "").strip()
    u = resp.usage

    print("[OK] 成功")
    print()
    print("模型回答   :", answer if answer else "(空)")
    print("消耗       :", f"输入 {u.prompt_tokens} + 输出 {u.completion_tokens} = {u.total_tokens} tokens")

    details = getattr(u, "completion_tokens_details", None)
    if details is not None:
        rt = getattr(details, "reasoning_tokens", None)
        if rt:
            print(f"             其中思考占 {rt} tokens")

    print()
    print("=" * 56)
    print("  三件事都对了：Key 有效、余额够、模型名正确")
    print("  下一步：运行  python chat.py  开始正式对话")
    print("=" * 56)


if __name__ == "__main__":
    main()
