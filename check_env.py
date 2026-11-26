# -*- coding: utf-8 -*-
"""
环境自检脚本
用法：  python check_env.py
目的：一次性确认所有东西装对了，不用猜。
"""
import sys
import os

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def line(char="-", n=56):
    print(char * n)


def main():
    line("=")
    print("  环境自检")
    line("=")
    print()

    # 1. Python 本体
    print("[1] Python 解释器")
    print("    版本 :", sys.version.split()[0])
    print("    路径 :", sys.executable)
    ok_py = sys.version_info[:2] == (3, 10)
    print("    预期 : 3.10  ->", "OK" if ok_py else "注意：版本不是 3.10，可能遇到包装不上的问题")
    print()

    # 2. 依赖包
    print("[2] 依赖包")
    packages = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("openai", "openai"),
        ("streamlit", "streamlit"),
    ]
    missing = []
    for name, mod in packages:
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "?")
            print(f"    {name:<12} {ver:<14} OK")
        except ImportError:
            print(f"    {name:<12} {'未安装':<12} 缺失")
            missing.append(name)
    print()

    # 3. 跑一次真实计算，确认 pandas 能用
    print("[3] 功能测试：pandas 实际运算")
    try:
        import pandas as pd

        df = pd.DataFrame(
            {
                "city": ["郑州", "郑州", "洛阳", "洛阳", "南阳"],
                "sales": [120, 180, 90, 110, 60],
            }
        )
        result = df.groupby("city")["sales"].sum().sort_values(ascending=False)
        print("    分组求和结果：")
        for city, val in result.items():
            print(f"      {city}: {val}")
        print("    -> pandas 工作正常")
    except Exception as e:
        print("    -> 出错：", e)
        missing.append("pandas")
    print()

    # 4. 中文字体（画图会用到）
    print("[4] 画图中文支持")
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
        plt.rcParams["axes.unicode_minus"] = False
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.set_title("中文测试")
        ax.plot([1, 2, 3], [1, 4, 2])
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_font_test.png")
        fig.savefig(out, dpi=80)
        plt.close(fig)
        print("    已生成 _font_test.png，打开看一眼标题有没有变成方块")
        print("    路径 :", out)
    except Exception as e:
        print("    -> 出错：", e)
    print()

    # 5. API Key
    print("[5] 大模型 API Key")
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if key:
        print("    已从环境变量读到 Key（前 6 位）：", key[:6] + "..." if len(key) > 6 else "过短")
    elif os.path.exists(env_file):
        print("    检测到 .env 文件，但未加载。需要 python-dotenv 或手动读取")
    else:
        print("    还没有配置。第 1 周任务 11.26 会做这件事")
        print("    做法：复制 .env.example 改名为 .env，把 Key 填进去")
    print()

    line("=")
    if missing:
        print("  还需要补：", ", ".join(missing))
        print("  修复命令：pip install " + " ".join(missing))
    else:
        print("  环境就绪。可以开始写代码了。")
    line("=")


if __name__ == "__main__":
    main()
