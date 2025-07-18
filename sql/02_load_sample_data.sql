-- ===================================================
-- 文件名：02_load_sample_data.sql
-- 功能：从本地导入数据并检查
-- 作者：qiyulu
-- 日期：2025-07-15
-- ===================================================

-- 从本地导入数据
load data local infile '/volumes/LULU/user-behavior-analysis/data/sample/sample_1000rows.csv'
into table taobao_behavior_sample
fields terminated by ','
lines terminated by '\n'
(user_id, item_id, category_id, behavior_type, ts);

-- 验证导入结果
use taobao_behavior_sample;

select count(*) as sample_count
from taobao_behavior_sample;

select *
from taobao_behavior_sample
limit 10;

-- 导入成功