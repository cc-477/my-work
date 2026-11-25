# -*- coding: utf-8 -*-
"""
SQL 入门 5 题（本地练习，不用联网、不用注册）

用法：双击 run_sql.bat，或者  .venv\\Scripts\\python.exe sql_practice.py

规则：
    - 输入 SQL，行尾打一个分号 ; 再回车，就会执行
    - 输入 hint   看提示
    - 输入 table  看表结构和数据
    - 输入 skip   跳过这题
    - 输入 exit   退出

每次运行都会重建数据库，随便写，写坏了不影响任何东西。
"""
import os
import sqlite3
import sys

try:
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- 数据
# 建两张表：company（公司）和 job（岗位）。
# 数据是照着郑州真实的 AI/数据岗抄的，不是编的。
SCHEMA = """
CREATE TABLE company (
    id       INTEGER PRIMARY KEY,
    name     TEXT,
    city     TEXT,
    industry TEXT
);

CREATE TABLE job (
    id         INTEGER PRIMARY KEY,
    title      TEXT,
    company_id INTEGER,
    salary_min INTEGER,   -- 月薪下限，单位元
    salary_max INTEGER,   -- 月薪上限，单位元
    edu        TEXT
);

INSERT INTO company VALUES
 (1,'吉客印数字科技','郑州','数字营销'),
 (2,'郑州数链科技','郑州','数据服务'),
 (3,'云和数据','郑州','大数据'),
 (4,'中科曙光郑州','郑州','云计算'),
 (5,'中原银行','郑州','银行'),
 (6,'洛阳LYC轴承','洛阳','制造'),
 (7,'河南投资集团','郑州','投资'),
 (8,'字节跳动','北京','互联网');

INSERT INTO job VALUES
 ( 1,'AI解决方案专员',   1,10000,15000,'本科'),
 ( 2,'Python数据分析师', 2, 8000,14000,'本科'),
 ( 3,'大数据分析师',     3, 7000,12000,'本科'),
 ( 4,'数据挖掘工程师',   4, 9000,15000,'本科'),
 ( 5,'数据分析师(零售)', 5, 7000,11000,'硕士'),
 ( 6,'数字化运营',       6, 6000, 9000,'本科'),
 ( 7,'投资分析岗',       7, 8000,12000,'硕士'),
 ( 8,'数据分析师-增长',  8,15000,25000,'本科'),
 ( 9,'AI产品经理',       1,12000,18000,'本科'),
 (10,'数据运营专员',     3, 6500, 9500,'大专'),
 (11,'报表开发',         5, 8000,13000,'本科'),
 (12,'算法工程师',       8,20000,35000,'硕士');
"""


# ---------------------------------------------------------------- 题目
TASKS = [
    {
        "q": "查出所有岗位的名称和最低薪资（只要这两列）。",
        "hint": "SELECT 后面写你要的列名，多个列用逗号隔开，FROM 后面写表名。\n"
                "        列名是 title 和 salary_min，表名是 job。",
        "ref": "SELECT title, salary_min FROM job",
    },
    {
        "q": "查出所有在郑州的岗位，按最低薪资从高到低排序。",
        "hint": "筛选行用 WHERE，条件是 city = '郑州'（字符串要加单引号）。\n"
                "        排序用 ORDER BY 列名 DESC，DESC 是从大到小。\n"
                "        注意：city 这一列在 company 表里，不在 job 表里——所以这题需要 JOIN。\n"
                "        如果暂时不会 JOIN，可以先试试只写 WHERE 看看报什么错，报错也是学习。",
        "ref": "SELECT job.title, job.salary_min FROM job JOIN company ON job.company_id = company.id "
               "WHERE company.city = '郑州' ORDER BY job.salary_min DESC",
    },
    {
        "q": "只看郑州，薪资最高的 3 个岗位是哪些？（显示岗位名和最低薪资）",
        "hint": "在上一题的基础上，最后加 LIMIT 3。\n"
                "        ORDER BY 必须在 LIMIT 前面，顺序写反会报错。",
        "ref": "SELECT job.title, job.salary_min FROM job JOIN company ON job.company_id = company.id "
               "WHERE company.city = '郑州' ORDER BY job.salary_min DESC LIMIT 3",
    },
    {
        "q": "每个城市分别有多少个岗位？（显示城市名和岗位数量，数量那一列叫 cnt）",
        "hint": "这题要分组：GROUP BY 城市，然后 COUNT(*) 数数量。\n"
                "        COUNT(*) AS cnt 意思是给这一列起名叫 cnt。\n"
                "        注意你按城市分组，但城市在 company 表里，还是要 JOIN。",
        "ref": "SELECT company.city, COUNT(*) AS cnt FROM job JOIN company ON job.company_id = company.id "
               "GROUP BY company.city",
    },
    {
        "q": "查出每个岗位的名称、公司名、公司所在城市（三列，一共 12 行）。",
        "hint": "JOIN 就是把两张表按某个共同的值拼起来。\n"
                "        写法：FROM job JOIN company ON job.company_id = company.id\n"
                "        ON 后面那句是拼接条件：岗位表里的 company_id 等于公司表里的 id。\n"
                "        拼好之后两张表的列都能直接用了。",
        "ref": "SELECT job.title, company.name, company.city FROM job "
               "JOIN company ON job.company_id = company.id",
    },
]


# ---------------------------------------------------------------- 工具
def wcwidth(s):
    """估算显示宽度，中文算 2 格，用来对齐表格。"""
    n = 0
    for ch in str(s):
        n += 2 if ord(ch) > 127 else 1
    return n


def pad(s, width):
    s = "" if s is None else str(s)
    return s + " " * max(0, width - wcwidth(s))


def print_table(cols, rows):
    if not rows:
        print("    （查出来是空的，一行都没有）")
        return
    widths = []
    for i, c in enumerate(cols):
        w = wcwidth(c)
        for r in rows:
            w = max(w, wcwidth(r[i]))
        widths.append(min(w, 28))

    print("    " + " | ".join(pad(c, widths[i]) for i, c in enumerate(cols)))
    print("    " + "-+-".join("-" * w for w in widths))
    for r in rows[:30]:
        print("    " + " | ".join(pad(v, widths[i]) for i, v in enumerate(r)))
    if len(rows) > 30:
        print("    ...（共 %d 行，只显示前 30 行）" % len(rows))


def norm(rows):
    """把结果整理成可比较的形式：按值排序，忽略列顺序无关的差异。"""
    return sorted(tuple("" if v is None else v for v in r) for r in rows)


def run_sql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    return cols, rows


def show_schema(conn):
    print("""
    ┌─ company 表（公司）──────────────────────────┐
    │  id        编号                              │
    │  name      公司名                            │
    │  city      城市                              │
    │  industry  行业                              │
    └──────────────────────────────────────────────┘
    ┌─ job 表（岗位）──────────────────────────────┐
    │  id          编号                            │
    │  title       岗位名                          │
    │  company_id  属于哪家公司（对应 company.id）  │
    │  salary_min  月薪下限                        │
    │  salary_max  月薪上限                        │
    │  edu         学历要求                        │
    └──────────────────────────────────────────────┘
""")
    print_table(*run_sql(conn, "SELECT * FROM company"))
    print()
    print_table(*run_sql(conn, "SELECT * FROM job"))


def ask_sql():
    """读一条 SQL，支持多行——遇到行尾分号才结束。"""
    buf = []
    while True:
        prompt = "    SQL> " if not buf else "     ... "
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        cmd = line.strip().lower().rstrip(";")
        if not buf and cmd in ("exit", "quit", "退出"):
            return "EXIT"
        if not buf and cmd == "hint":
            return "HINT"
        if not buf and cmd == "table":
            return "TABLE"
        if not buf and cmd == "skip":
            return "SKIP"
        if not line.strip():
            continue
        buf.append(line)
        if line.rstrip().endswith(";"):
            return "\n".join(buf)


def main():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)

    print("=" * 62)
    print("  SQL 入门 5 题 · 本地练习")
    print("=" * 62)
    print("  数据是郑州真实的 AI/数据岗，两张表：company（公司）、job（岗位）")
    print("  命令： hint 看提示 | table 看数据 | skip 跳过 | exit 退出")
    print()
    print("  规则：SQL 写完在行尾打一个分号 ; 再回车才会执行")
    print("        分号忘了它就会一直等你，一直等不到就按 Ctrl+C 重来")
    print()

    passed = 0
    for i, task in enumerate(TASKS, 1):
        print("-" * 62)
        print("  第 %d 题（共 %d 题）" % (i, len(TASKS)))
        print()
        print("  " + task["q"])
        print("-" * 62)

        ref_cols, ref_rows = run_sql(conn, task["ref"])

        while True:
            sql = ask_sql()
            if sql is None or sql == "EXIT":
                print()
                print("  提前结束。做了 %d 题，其中 %d 题通过。" % (i - 1, passed))
                return
            if sql == "HINT":
                print("    提示：" + task["hint"])
                print()
                continue
            if sql == "TABLE":
                show_schema(conn)
                continue
            if sql == "SKIP":
                print("    跳过。参考答案：")
                print("    " + task["ref"])
                print()
                break

            try:
                cols, rows = run_sql(conn, sql)
            except sqlite3.Error as e:
                print("    [报错] %s" % e)
                print("    报错是正常的，看它说的哪个词不认识，改那个词。看不懂就输 hint。")
                print()
                continue

            print()
            print_table(cols, rows)
            print()

            if norm(rows) == norm(ref_rows):
                passed += 1
                print("    ✓ 通过。这一题的结果是对的。")
                if "ORDER BY" not in sql.upper() and "order by" in task["ref"].lower():
                    print("      （顺便说：参考答案里要求排序，你这题没排序但结果一致，算过）")
                print()
                break
            else:
                print("    还不对。你查出 %d 行，正确答案是 %d 行。" % (len(rows), len(ref_rows)))
                if len(rows) == len(ref_rows):
                    print("    行数一样但内容不同 —— 多半是某一列选错了，或者条件写错了。")
                elif len(rows) > len(ref_rows):
                    print("    行多了 —— 筛选条件不够严，或者 JOIN 之后重复了。")
                else:
                    print("    行少了 —— 筛选条件太严，或者 JOIN 把该匹配的漏掉了。")
                print("    再试一次，或者输 hint。")
                print()

    print("=" * 62)
    print("  做完 5 题，通过 %d 题。" % passed)
    if passed == 5:
        print("  全过了。下一步：把这两个文件传上 GitHub（我们下次弄）。")
    elif passed >= 3:
        print("  过得去的水平。没过的题明天再做一遍，别看答案。")
    else:
        print("  今天先到这。没过的题明天重来，做题靠的是动手次数，不是看懂次数。")
    print("=" * 62)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  已中断。")
    except Exception:
        import traceback
        print()
        print("=" * 62)
        print("  出错了，下面是原因：")
        print("=" * 62)
        traceback.print_exc()
        try:
            input("\n按回车键关闭...")
        except Exception:
            pass
