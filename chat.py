# -*- coding: utf-8 -*-
"""
第一个 AI 对话脚本
用法：  python chat.py
前提：  .env 里已经填好 DEEPSEEK_API_KEY

命令：
    直接输入问题        对话
    /think              切换思考模式（更准，但更慢更贵）
    exit                退出

每一行都有注释，看不懂的地方问 AI，不要跳过。
"""
import os
import sys

try:
    # 管道/重定向时用 utf-8；直接双击的控制台保持系统默认，中文才不会乱
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from openai import OpenAI
except ImportError:
    print("=" * 58)
    print("  启动方式不对：这个 Python 里没有 openai")
    print("=" * 58)
    print()
    print("你当前使用的 Python：", sys.version.split()[0])
    print("它的位置：", sys.executable)
    print()
    print("原因：直接双击 chat.py 时，Windows 会用系统默认的 Python 打开，")
    print("      而依赖包装在项目自己的 .venv 里，两者不是同一个。")
    print()
    print("正确做法：不要双击 chat.py，改双击同目录下的 run_chat.bat")
    print()
    try:
        input("按回车键关闭...")
    except Exception:
        pass
    sys.exit(1)


MODEL = "deepseek-flash"          # 2026年11月现役模型名，旧的 deepseek-chat 已于 7 月停用
BASE_URL = "https://api.deepseek.com"


def load_key():
    """从 .env 文件里读出密钥。不装额外依赖，手写解析。"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        print("找不到 .env 文件。")
        print("做法：运行 python set_key.py 写入你的 Key。")
        sys.exit(1)

    with open(env_path, "r", encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "DEEPSEEK_API_KEY":
                v = v.strip().strip('"').strip("'")
                if not v or "你的密钥" in v:
                    print("Key 还是占位符。运行 python set_key.py 重新写入。")
                    sys.exit(1)
                return v

    print(".env 里没找到 DEEPSEEK_API_KEY 这一行。")
    sys.exit(1)


def load_prompt():
    """
    system 提示词放在同目录的 prompt.txt 里，方便改，不用动代码。
    改了 prompt.txt 保存后，重新运行 chat.py 就生效。
    """
    default = "你是一个耐心的助教，回答简洁，多用例子。"
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompt.txt")
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        text = f.read().strip()
    return text if text else default


def main():
    api_key = load_key()
    client = OpenAI(api_key=api_key, base_url=BASE_URL)

    # 对话历史。模型本身不记事，每次都要把前面说过的话一起发过去
    system_prompt = load_prompt()
    history = [
        {"role": "system", "content": system_prompt}
    ]

    state = {"thinking": False}

    def show_mode():
        if state["thinking"]:
            print("  >>> 当前：思考模式（模型先推理再回答，更准，更慢更贵）")
        else:
            print("  >>> 当前：快速模式（直接回答，便宜）")

    print("=" * 56)
    print("  已连接 " + MODEL)
    print("  输入问题对话  |  /think 切换思考模式  |  exit 退出")
    print("-" * 56)
    print("  当前身份： " + system_prompt.splitlines()[0][:40])
    print("  （想换身份，改 prompt.txt 后重新运行）")
    print("=" * 56)
    show_mode()

    total_tokens = 0
    total_reasoning = 0

    while True:
        try:
            question = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in ("exit", "quit", "退出"):
            break
        if question == "/think":
            state["thinking"] = not state["thinking"]
            show_mode()
            continue

        history.append({"role": "user", "content": question})

        # 思考模式下必须给足 max_tokens，否则推理会把额度吃光，正文变空
        kwargs = {
            "model": MODEL,
            "messages": history,
            "temperature": 0.7,          # 0 最稳定，1 最发散
            "max_tokens": 2000 if state["thinking"] else 800,
        }
        if not state["thinking"]:
            kwargs["extra_body"] = {"thinking": {"type": "disabled"}}

        try:
            resp = client.chat.completions.create(**kwargs)
        except Exception as e:
            err = str(e)
            print("\n调用失败：", err)
            if "401" in err or "auth" in err.lower():
                print("-> 密钥有问题。检查 .env 里是不是以 sk- 开头，前后有没有多空格。")
            elif "402" in err or "balance" in err.lower() or "insufficient" in err.lower():
                print("-> 余额不足。去 platform.deepseek.com 充值，最低 10 元。")
            elif "404" in err or "model" in err.lower():
                print("-> 模型名不对。当前应该是 " + MODEL)
            elif "429" in err:
                print("-> 请求太频繁，等几秒再试。")
            else:
                print("-> 其他错误，把上面这行原文复制给 AI 让它帮你判断。")
            history.pop()  # 把这轮问题撤掉，避免污染历史
            continue

        reply = resp.choices[0].message
        reasoning = getattr(reply, "reasoning_content", None)

        # 思考模式下，把模型内部的推理过程露出来看看，这是理解大模型最直接的方式
        if reasoning:
            preview = reasoning.strip().replace("\n", " ")
            if len(preview) > 280:
                preview = preview[:280] + "..."
            print("\n  [思考] " + preview)

        answer = (reply.content or "").strip()
        if answer:
            print("\nAI：" + answer)
        else:
            print("\nAI：（模型没有输出正文。思考可能占满了额度，试试 /think 关掉思考，或把问题问短一点）")

        # 把回答也存进历史，这样它下一轮能记得自己说过什么
        history.append({"role": "assistant", "content": answer or "(空)"})

        # 打印这轮消耗了多少 token，养成看成本的习惯
        u = resp.usage
        total_tokens += u.total_tokens
        details = getattr(u, "completion_tokens_details", None)
        r_tokens = getattr(details, "reasoning_tokens", 0) if details else 0
        if r_tokens:
            total_reasoning += r_tokens
            print(f"\n  [本轮 {u.prompt_tokens} 进 + {u.completion_tokens} 出（思考 {r_tokens}）= {u.total_tokens}，累计 {total_tokens}]")
        else:
            print(f"\n  [本轮 {u.prompt_tokens} 进 + {u.completion_tokens} 出 = {u.total_tokens}，累计 {total_tokens}]")

    print(f"\n对话结束。累计 {total_tokens} tokens，其中思考消耗 {total_reasoning}。")


if __name__ == "__main__":
    # 包一层兜底：任何意外错误都要停住，把原因显示出来，绝不闪退
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已中断。")
    except Exception:
        import traceback
        print()
        print("=" * 58)
        print("  出错了。下面这段就是原因：")
        print("=" * 58)
        traceback.print_exc()
        print()
        print("处理办法：把上面这段红字全部复制给 AI，说「我是初学者，解释这个错误")
        print("并给我改好的完整代码」，它会告诉你哪一行有问题。")
        try:
            input("\n按回车键关闭...")
        except Exception:
            pass
        sys.exit(1)
