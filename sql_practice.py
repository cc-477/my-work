# -*- coding: utf-8 -*-
"""
SQL 入门 5 题（第一批，本地练习）

用法：双击 run_sql.bat，或者  .venv\\Scripts\\python.exe sql_practice.py

规则：
    - 输入 SQL，行尾打一个分号 ; 再回车，就会执行
    - 输入 hint   看提示
    - 输入 table  看表结构和数据
    - 输入 skip   跳过这题
    - 输入 exit   退出

每次运行都会重建数据库，随便写，写坏了不影响任何东西。
"""
import json
import os
import sqlite3
import sys

try:
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ---------------------------------------------------------------- 进度存档
# 关掉窗口不用怕：做到哪一题会写进一个小文件，下次启动自动接上。
def load_progress(path):
    """返回 (下一题的题号, 已通过的题号列表)。读不到就当没做过。"""
    if not path:
        return 1, []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        nxt = int(data.get("next", 1))
        done = [int(x) for x in data.get("passed", [])]
        return max(nxt, 1), done
    except Exception:
        return 1, []


def save_progress(path, next_q, passed_list):
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"next": next_q, "passed": sorted(set(passed_list))}, f)
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
    """把结果整理成可比较的形式：按值排序，忽略顺序差异。"""
    return sorted(tuple("" if v is None else v for v in r) for r in rows)


def run_sql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    return cols, rows


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


def run_tasks(conn, tasks, title, intro, schema_fn, start=None, progress_path=None):
    """跑一批题，返回本次通过的题数。两个练习文件共用这一套逻辑。

    start: 从第几题开始。None = 自动接上次进度；给数字 = 强制从那里开始。
    progress_path: 进度存档文件路径。给了就会自动记住做到哪、通过了哪几题。
    """
    saved_next, done_list = load_progress(progress_path)

    if start is None:
        start = saved_next
        resumed = start > 1
    else:
        start = max(int(start), 1)
        resumed = False
        if start == 1:
            done_list = []   # 从头重做，清空旧的通过记录

    if start > len(tasks):
        start = 1
        resumed = False
        done_list = []
        fresh_all = True
    else:
        fresh_all = False

    print("=" * 62)
    print("  " + title)
    print("=" * 62)
    for line in intro:
        print("  " + line)
    print("  命令： hint 看提示 | table 看数据 | skip 跳过 | exit 退出")
    print()
    print("  规则：SQL 写完在行尾打一个分号 ; 再回车才会执行")
    print("        分号忘了它就会一直等你，等不到就按 Ctrl+C 重来")
    print()

    if fresh_all:
        print("  上次这批题已经全部做完了。从头再来一遍。")
        print()
    elif resumed:
        print("  接上次进度：现在从第 %d 题开始（之前已通过 %d 题）。"
              % (start, len(done_list)))
        print("  想从头重做，就输入 exit 退出，再启动时在题号那里填 1。")
        print()
    elif start > 1:
        print("  从第 %d 题开始（前 %d 题已跳过）" % (start, start - 1))
        print()

    passed = 0
    for i, task in enumerate(tasks, 1):
        if i < start:
            continue
        print("-" * 62)
        print("  第 %d 题（共 %d 题）" % (i, len(tasks)))
        print()
        print("  " + task["q"])
        print("-" * 62)

        ref_cols, ref_rows = run_sql(conn, task["ref"])

        while True:
            sql = ask_sql()
            if sql is None or sql == "EXIT":
                print()
                save_progress(progress_path, i, done_list)
                print("  提前结束。本次做了 %d 题，通过 %d 题。"
                      % (i - start, passed))
                print("  下次启动会自动从第 %d 题接上。" % i)
                return passed
            if sql == "HINT":
                print("    提示：" + task["hint"])
                print()
                continue
            if sql == "TABLE":
                schema_fn(conn)
                continue
            if sql == "SKIP":
                print("    跳过。参考答案：")
                print("    " + task["ref"])
                print()
                save_progress(progress_path, i + 1, done_list)
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
                if i not in done_list:
                    done_list.append(i)
                print("    ✓ 通过。这一题的结果是对的。")
                if "order by" in task["ref"].lower() and "order by" not in sql.lower():
                    print("      （你这题没写 ORDER BY，结果碰巧一致。排序的题自己要记得写）")
                print()
                save_progress(progress_path, i + 1, done_list)
                break

            print("    还不对。你查出 %d 行，正确答案是 %d 行。" % (len(rows), len(ref_rows)))
            if len(rows) == len(ref_rows):
                print("    行数一样但内容不同 —— 多半是某一列选错了，或者条件写错了。")
            elif len(rows) > len(ref_rows):
                print("    行多了 —— 筛选条件不够严，或者 JOIN 之后重复了。")
            else:
                print("    行少了 —— 筛选条件太严，或者 JOIN 把该匹配的漏掉了。")
            print("    再试一次，或者输 hint。")
            print()

    save_progress(progress_path, len(tasks) + 1, done_list)
    return passed


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


def main():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)

    here = os.path.dirname(os.path.abspath(__file__))
    start = None
    if len(sys.argv) >= 2 and str(sys.argv[1]).strip():
        try:
            start = int(str(sys.argv[1]).strip())
        except ValueError:
            print("  参数看不懂：%r，将自动接上次进度。用法：python sql_practice.py 3"
                  % sys.argv[1])
            start = None

    passed = run_tasks(
        conn, TASKS,
        "SQL 入门 5 题 · 本地练习（第一批）",
        ["数据是郑州真实的 AI/数据岗，两张表：company（公司）、job（岗位）"],
        show_schema,
        start=start,
        progress_path=os.path.join(here, ".progress_sql1.json"),
    )

    print("=" * 62)
    _, done_total = load_progress(os.path.join(here, ".progress_sql1.json"))
    print("  本次通过 %d 题，累计通过 %d / %d 题。"
          % (passed, len(done_total), len(TASKS)))
    if len(done_total) == len(TASKS):
        print("  全过了。下一步：双击 run_sql2.bat 做第二批（聚合分组与多表 JOIN）。")
    elif len(done_total) >= 3:
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
