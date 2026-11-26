-- 第 2 批 SQL 练习（2026-11-25）：聚合分组与多表 JOIN
-- 数据库：sql_practice2.py 里的内存库
--   company(id, name, city, industry)
--   job(id, title, company_id, salary_min, salary_max, edu)
--   skill(id, job_id, skill_name)
--
-- 每题下面两条：先是我自己写的，再是参考答案。
-- 对比两条的差别，比只看答案有用。


-- ------------------------------------------------------------------
-- 第 1 题：每个城市的平均最低薪资，取整，按平均薪资从高到低
SELECT company.city, ROUND(AVG(job.salary_min)) AS avg_min
FROM job
JOIN company ON job.company_id = company.id
GROUP BY company.city
ORDER BY avg_min DESC;

-- 要点：SELECT 里出现的非聚合列（city）必须出现在 GROUP BY 里，
--       否则不同数据库给的结果不一样，MySQL 严格模式会直接报错。


-- ------------------------------------------------------------------
-- 第 2 题：岗位数量 >= 3 的公司
SELECT company.name, COUNT(*) AS cnt
FROM job
JOIN company ON job.company_id = company.id
GROUP BY company.name
HAVING COUNT(*) >= 3;

-- 要点：筛"组"用 HAVING，筛"行"用 WHERE。
--       WHERE 在 GROUP BY 之前执行，所以它里面不能出现聚合函数。


-- ------------------------------------------------------------------
-- 第 3 题：每种学历要求下最高月薪上限
SELECT edu, MAX(salary_max) AS max_top
FROM job
GROUP BY edu;

-- 要点：这题不需要 JOIN —— 要用的两列在同一张表里。
--       先看数据在哪张表，再决定要不要连表，别条件反射地 JOIN。


-- ------------------------------------------------------------------
-- 第 4 题：只看本科岗位，平均最低薪资超过 9000 的公司
SELECT company.name, ROUND(AVG(job.salary_min)) AS avg_min
FROM job
JOIN company ON job.company_id = company.id
WHERE job.edu = '本科'
GROUP BY company.name
HAVING AVG(job.salary_min) > 9000;

-- 要点：两层过滤同时出现时的顺序
--       WHERE（过行） -> GROUP BY（分组） -> HAVING（过组）
--       写反了不报错，只是结果会变。


-- ------------------------------------------------------------------
-- 第 5 题：每家公司的岗位数，没有岗位的也要列出来显示 0
SELECT company.name, COUNT(job.id) AS cnt
FROM company
LEFT JOIN job ON job.company_id = company.id
GROUP BY company.name;

-- 要点：LEFT JOIN 保留左表全部行，右边配不上就填 NULL。
--       这里必须写 COUNT(job.id)，不能写 COUNT(*)：
--         COUNT(*)       数的是行数，空行也算 1
--         COUNT(列名)    跳过 NULL，所以没岗位的才是 0
--       这个错不报错，结果从 0 变成 1 —— 最难发现的那种错。


-- ------------------------------------------------------------------
-- 第 6 题：要求 SQL 技能的岗位（岗位名 + 公司名）
SELECT job.title, company.name
FROM job
JOIN skill ON skill.job_id = job.id
JOIN company ON job.company_id = company.id
WHERE skill.skill_name = 'SQL';

-- 要点：JOIN 可以连着写多个，每多一张表就多一个 ON。
--       连接顺序不影响结果（内连接满足交换律），但这题从 job 出发最自然：
--       job 是中心表，skill 和 company 都挂在它上面。


-- ------------------------------------------------------------------
-- 补充：同一道题用旧写法也能写出来（逗号 + WHERE）
-- 第 6 题等价的旧写法：
--   SELECT job.title, company.name
--   FROM job, skill, company
--   WHERE skill.job_id = job.id
--     AND job.company_id = company.id
--     AND skill.skill_name = 'SQL';
-- 两种写法内连接结果一样，但 JOIN ... ON 更清楚：连接条件和筛选条件分开了。
-- 而且 LEFT JOIN 没有旧写法，只能写 JOIN ... ON，所以早点习惯这一种。
