-- summarize the count of lab tests, each additionally categorized by the units
with
table1 as (select itemid from labevents group by itemid order by count(*) desc),
table2 as (select itemid, valueuom, count(*) as n from labevents group by itemid, valueuom)
select table2.itemid, table2.valueuom, table2.n from table1 left join table2 on table1.itemid=table2.itemid;


-- summarize the mean of lab tests, each additionally categorized by the units; skip non quantitative tests
with
table1 as (select itemid from labevents where valuenum IS NOT NULL group by itemid order by count(*) desc),
table2 as (select itemid, valueuom, avg(valuenum) as mean, count(*) as n from labevents where valuenum IS NOT NULL group by itemid, valueuom)
select table2.itemid, table2.valueuom, table2.n, table2.mean from table1 left join table2 on table1.itemid=table2.itemid;
