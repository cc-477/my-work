# -*- coding: utf-8 -*-
"""
一键写入 API Key
用法：  python set_key.py
特点：  输入时不显示内容（防止旁边有人看到），自动清理空格、引号、BOM
"""
import os
import sys
import re
import getpass

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
KEY_NAME = "DEEPSEEK_API_KEY"


def read_lines():
    if not os.path.exists(ENV_PATH):
        print("[X] 找不到 .env 文件，先确认它和本脚本在同一个文件夹")
        sys.exit(1)
    with open(ENV_PATH, "r", encoding="utf-8-sig") as f:
        return f.read().splitlines()


def clean(raw):
    """把用户粘贴进来的东西洗干净：去首尾空白、去掉误带的引号和中文标点"""
    s = raw.strip()
    s = s.strip('"').strip("'")
    s = s.replace("\u3000", "").replace(" ", "")
    return s


def main():
    print("=" * 56)
    print("  写入 API Key")
    print("=" * 56)
    print()
    print("去 platform.deepseek.com -> API keys -> 创建，复制那串 sk- 开头的字符")
    print("粘贴到这里，按回车。输入过程不会显示，这是正常的。")
    print()

    try:
        raw = getpass.getpass("请粘贴 Key：")
    except (KeyboardInterrupt, EOFError):
        print("\n已取消")
        sys.exit(1)

    key = clean(raw)

    # 常见误操作检查
    if not key:
        print("\n[X] 什么都没输入")
        sys.exit(1)
    if "你的密钥" in key or key == "sk-":
        print("\n[X] 还是模板里的占位符，请换成平台上复制的那串真实 Key")
        sys.exit(1)
    if not key.startswith("sk-"):
        print("\n[!] 注意：正常 Key 应该以 sk- 开头，你输入的是以", key[:3], "开头")
        print("    仍然继续，但很可能不对。")
    if len(key) < 20:
        print(f"\n[X] 长度只有 {len(key)} 位，明显不完整（正常 30-60 位）")
        print("    可能复制时漏了，重新复制一次")
        sys.exit(1)

    print()
    print(f"读到 {len(key)} 位，开头 {key[:6]}...结尾 ...{key[-4:]}")
    print("（只显示首尾，完整内容不会出现在屏幕上）")
    print()

    lines = read_lines()
    out = []
    replaced = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or "=" not in stripped:
            out.append(line)
            continue
        name = stripped.split("=", 1)[0].strip()
        if name == KEY_NAME:
            out.append(f"{KEY_NAME}={key}")
            replaced = True
        else:
            out.append(line)

    if not replaced:
        out.append(f"{KEY_NAME}={key}")

    with open(ENV_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")

    print("[OK] 已写入 .env")
    print()

    # 顺手检查有没有把 Key 写进了会提交的文件
    for bad in ["chat.py", ".env.example"]:
        p = os.path.join(os.path.dirname(ENV_PATH), bad)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8-sig", errors="ignore") as f:
                if key in f.read():
                    print(f"[!] 警告：{bad} 里也出现了这个 Key，必须删掉，否则会泄露")

    print("下一步：运行  python test_api.py  验证是否通")
    print("=" * 56)


if __name__ == "__main__":
    main()
