-- calculate lab summary of quantitative lab findings
WITH
-- order lab test by their total counts
table1 AS (SELECT itemid FROM labevents WHERE valuenum IS NOT NULL GROUP BY itemid ORDER BY count(*) DESC),
-- compute mean and count of each unit for every lab test
table2 AS (SELECT itemid, valueuom, avg(valuenum) AS mean, count(*) AS n FROM labevents WHERE valuenum IS NOT NULL GROUP BY itemid, valueuom),
-- compute the min, mean and max of normal lab tests
table3 AS (SELECT itemid, valueuom, min(valuenum) AS minimum, avg(valuenum) AS mean, max(valuenum) AS maximum FROM labevents  WHERE valuenum IS NOT NULL AND (flag IS NULL OR UPPER(flag)!='ABNORMAL') GROUP BY itemid, valueuom),
table23 AS (SELECT table2.itemid AS itemid, table2.valueuom AS valueuom, table2.n AS counts, table2.mean AS mean_all, table3.minimum AS min_normal,table3.mean AS mean_normal, table3.maximum AS max_normal FROM table2 LEFT JOIN table3 ON  table2.itemid=table3.itemid AND table2.valueuom=table3.valueuom)
SELECT table23.itemid, table23.valueuom, table23.counts, table23.mean_all, table23.min_normal, table23.mean_normal, table23.max_normal FROM table1 LEFT JOIN table23 ON  table1.itemid=table23.itemid;

-- count non numeric values
SELECT value, count(value) AS n FROM labevents  WHERE valuenum IS NULL group by value having n > 100 ORDER BY n desc;