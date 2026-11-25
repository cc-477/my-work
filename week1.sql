-- 第 1 周 SQL 练习（2026-11-25）
-- 数据库：sql_practice.py 里的内存库
--   company(id, name, city, industry)
--   job(id, title, company_id, salary_min, salary_max, edu)
--
-- 做完之后，把上面 5 条 SQL 贴到下面的空行里。
-- 卡住看过答案的，在--后面写一句为什么卡，这个比答案本身有用。


-- 第 1 题：查出所有岗位的名称和最低薪资（只要这两列）
 select title,salary_min from job;


-- 第 2 题：查出所有在郑州的岗位，按最低薪资从高到低排序
select title,salary_min from job,company where job.company_id=company.id and city='郑州' order by salary_min desc;


-- 第 3 题：只看郑州，薪资最高的 3 个岗位
 select title,salary_min from job,company where job.company_id=company.id and city='郑州' order by salary_min desc limit 3;


-- 第 4 题：每个城市分别有多少个岗位（城市名 + 数量 cnt）
select city,count(title) from  job,company where job.company_id=company.id group by city;


-- 第 5 题：每个岗位的名称、公司名、公司所在城市（三列，12 行）

select title,name,city from job,company where job.company_id=company.id;
