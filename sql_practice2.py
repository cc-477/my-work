# -*- coding: utf-8 -*-
"""
SQL 第二批 · 聚合分组与多表 JOIN（6 题）

用法：双击 run_sql2.bat，或者  .venv\\Scripts\\python.exe sql_practice2.py

这批题对应两个能力：
    - 聚合：COUNT / SUM / AVG / MAX + GROUP BY + HAVING
    - 多表：三张表 JOIN，以及 LEFT JOIN 的"保留左边"特性

规则同第一批：分号结尾、hint 看提示、table 看数据、skip 跳过、exit 退出。
"""
import os
import sqlite3
import sys

try:
    if not sys.stdout.isatty():
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 复用第一批写好的判定逻辑，避免重复代码
from sql_practice import run_tasks, run_sql, print_table, load_progress


# ---------------------------------------------------------------- 数据
# 比第一批多两处设计：
#   1. 多了一张 skill 表（岗位要求的技能），用来练三表 JOIN
#   2. company 里多了一家「河南大数据中心」，它没有任何岗位，用来练 LEFT JOIN
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
    salary_min INTEGER,
    salary_max INTEGER,
    edu        TEXT
);

CREATE TABLE skill (
    id         INTEGER PRIMARY KEY,
    job_id     INTEGER,   -- 对应 job.id
    skill_name TEXT
);

INSERT INTO company VALUES
 (1,'吉客印数字科技','郑州','数字营销'),
 (2,'郑州数链科技','郑州','数据服务'),
 (3,'云和数据','郑州','大数据'),
 (4,'中科曙光郑州','郑州','云计算'),
 (5,'中原银行','郑州','银行'),
 (6,'洛阳LYC轴承','洛阳','制造'),
 (7,'河南投资集团','郑州','投资'),
 (8,'字节跳动','北京','互联网'),
 (9,'河南大数据中心','郑州','政务');

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
 (12,'算法工程师',       8,20000,35000,'硕士'),
 (13,'数据标注主管',     1, 8000,11000,'大专'),
 (14,'风控建模',         8,18000,30000,'硕士');

INSERT INTO skill VALUES
 ( 1, 1,'SQL'),   ( 2, 1,'Prompt'), ( 3, 1,'RAG'),
 ( 4, 2,'Python'),( 5, 2,'SQL'),    ( 6, 2,'pandas'),
 ( 7, 8,'SQL'),   ( 8, 8,'A/B测试'),( 9, 8,'Python'),
 (10,12,'Python'),(11,12,'PyTorch'),
 (12,14,'SQL'),   (13,14,'建模'),   (14,14,'Python');
"""


# ---------------------------------------------------------------- 题目
TASKS = [
    {
        "q": "每个城市的平均最低薪资是多少？取整，按平均薪资从高到低排。"
             "（显示城市、平均最低薪资 avg_min）",
        "hint": "平均值用 AVG(列名)，取整用 ROUND(值) 或 ROUND(值, 0)。\n"
                "        写法：SELECT city, ROUND(AVG(salary_min)) AS avg_min ...\n"
                "        分组：GROUP BY 城市。城市在 company 表里，还是要 JOIN。\n"
                "        最后 ORDER BY avg_min DESC。",
        "ref": "SELECT company.city, ROUND(AVG(job.salary_min)) AS avg_min "
               "FROM job JOIN company ON job.company_id = company.id "
               "GROUP BY company.city ORDER BY avg_min DESC",
    },
    {
        "q": "哪些公司招的岗位数量达到 3 个及以上？（显示公司名和岗位数 cnt）",
        "hint": "分组之后要过滤「组」，不能用 WHERE，必须用 HAVING。\n"
                "        WHERE 过滤的是行，HAVING 过滤的是组——这是本周最重要的一个区别。\n"
                "        写法：GROUP BY company.name HAVING COUNT(*) >= 3",
        "ref": "SELECT company.name, COUNT(*) AS cnt "
               "FROM job JOIN company ON job.company_id = company.id "
               "GROUP BY company.name HAVING COUNT(*) >= 3",
    },
    {
        "q": "每种学历要求下，最高的月薪上限是多少？（显示学历 edu、最高上限 max_top）",
        "hint": "最大值用 MAX(列名)。\n"
                "        这题不需要 JOIN，因为 edu 和 salary_max 都在 job 表里。\n"
                "        列表：SELECT edu, MAX(salary_max) AS max_top FROM job GROUP BY edu",
        "ref": "SELECT edu, MAX(salary_max) AS max_top FROM job GROUP BY edu",
    },
    {
        "q": "只看学历要求为「本科」的岗位，哪几家公司的平均最低薪资超过 9000？"
             "（显示公司名和平均薪资 avg_min）",
        "hint": "这题两层过滤，容易混：\n"
                "        ① 只看本科岗位 —— 这是过滤行，用 WHERE job.edu = '本科'\n"
                "        ② 平均薪资超过 9000 —— 这是过滤组，用 HAVING AVG(...) > 9000\n"
                "        顺序：WHERE 在 GROUP BY 前面，HAVING 在 GROUP BY 后面。",
        "ref": "SELECT company.name, ROUND(AVG(job.salary_min)) AS avg_min "
               "FROM job JOIN company ON job.company_id = company.id "
               "WHERE job.edu = '本科' GROUP BY company.name "
               "HAVING AVG(job.salary_min) > 9000",
    },
    {
        "q": "列出每家公司的岗位数量，一个岗位都没有的公司也要列出来，数量显示 0。"
             "（显示公司名和岗位数 cnt）",
        "hint": "这题要用 LEFT JOIN：FROM company LEFT JOIN job ON ...\n"
                "        LEFT JOIN 的意思是「左边那张表全部保留」，右边匹配不上就填空。\n"
                "        陷阱：不能写 COUNT(*)，那会把「没岗位」也数成 1 行。\n"
                "        要写 COUNT(job.id) —— 只数右边真实存在的行，空的会被忽略，结果才是 0。",
        "ref": "SELECT company.name, COUNT(job.id) AS cnt "
               "FROM company LEFT JOIN job ON job.company_id = company.id "
               "GROUP BY company.name",
    },
    {
        "q": "哪些岗位要求「SQL」这个技能？显示岗位名和公司名。",
        "hint": "三张表 JOIN，一步一步接：\n"
                "        FROM job\n"
                "        JOIN skill   ON skill.job_id = job.id\n"
                "        JOIN company ON job.company_id = company.id\n"
                "        然后 WHERE skill.skill_name = 'SQL'。\n"
                "        注意 JOIN 是可以连着写多个的，每多一张表就多一个 ON。",
        "ref": "SELECT job.title, company.name "
               "FROM job JOIN skill ON skill.job_id = job.id "
               "JOIN company ON job.company_id = company.id "
               "WHERE skill.skill_name = 'SQL'",
    },
]


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
    ┌─ skill 表（技能要求）────────────────────────┐
    │  id          编号                            │
    │  job_id      属于哪个岗位（对应 job.id）      │
    │  skill_name  技能名                          │
    └──────────────────────────────────────────────┘
""")
    print_table(*run_sql(conn, "SELECT * FROM company"))
    print()
    print_table(*run_sql(conn, "SELECT * FROM job"))
    print()
    print_table(*run_sql(conn, "SELECT * FROM skill"))


def parse_start(argv):
    """从命令行取「从第几题开始」。不带参数 = None，表示自动接上次进度。"""
    if len(argv) < 2:
        return None
    raw = str(argv[1]).strip()
    if not raw:
        return None
    try:
        n = int(raw)
    except ValueError:
        print("  参数看不懂：%r，将自动接上次进度。用法：python sql_practice2.py 6" % raw)
        return None
    if n < 1 or n > len(TASKS):
        print("  题号超出范围（共 %d 题），将从第 1 题开始。" % len(TASKS))
        return 1
    return n


def main():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)

    start = parse_start(sys.argv)
    here = os.path.dirname(os.path.abspath(__file__))

    passed = run_tasks(
        conn, TASKS,
        "SQL 第二批 · 聚合分组与多表 JOIN（6 题）",
        [
            "三张表：company（公司）、job（岗位）、skill（岗位要求的技能）",
            "注意 company 里有一家「河南大数据中心」没有任何岗位，第 5 题会用到它",
            "进度会自动记住：关了窗口再打开，从上次那一题接着做",
        ],
        show_schema,
        start=start,
        progress_path=os.path.join(here, ".progress_sql2.json"),
    )

    print("=" * 62)
    _, done_total = load_progress(os.path.join(here, ".progress_sql2.json"))
    print("  本次通过 %d 题，累计通过 %d / %d 题。"
          % (passed, len(done_total), len(TASKS)))
    if len(done_total) == len(TASKS):
        print("  全过了。这两批题覆盖了 SELECT / WHERE / ORDER BY / LIMIT /")
        print("  GROUP BY / HAVING / 多表 JOIN / LEFT JOIN —— 面试问的 SQL 基本就这些。")
        print("  下一步可以去牛客网对照刷一遍，验收自己是不是真的会了。")
    elif len(done_total) >= 4:
        print("  过得去。没过的那几题是薄弱点，明天重做一遍再去牛客。")
    else:
        print("  这批题比第一批难一档，卡住是正常的。没过的明天重来，别看答案。")
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
