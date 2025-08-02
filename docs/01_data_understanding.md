1. 字段预览
原始数据表 taobao_behavior 包含以下字段：
| 字段名             | 类型      | 说明                      |
| --------------- | ------- | ----------------------- |
| `user_id`       | BIGINT  | 用户唯一标识                  |
| `item_id`       | BIGINT  | 商品唯一标识                  |
| `category_id`   | BIGINT  | 商品所属类目 ID               |
| `behavior_type` | VARCHAR | 用户行为类型（pv/buy/cart/fav） |
| `ts`            | BIGINT  | 行为发生时间（Unix 时间戳）        |

字段命名在建表阶段即采用英文，符合可读性和命名规范。字段类型初步设定为 BIGINT 和 VARCHAR，为后续的数据清洗和结构优化提供灵活性。时间戳字段 ts 将在后续转换为可读格式字段 event_time，以便时间分析

2. 数据总量
共100,150,807条记录
数据量庞大，为后续行为模式建模和用户细分提供了丰富样本

3. 行为类型分布
SELECT behavior_type, COUNT(*) AS count
FROM taobao_behavior_original
GROUP BY behavior_type

UNION ALL

SELECT 'TOTAL' AS behavior_type, COUNT(*) AS count
FROM taobao_behavior_original

ORDER BY behavior_type;

结果:
"behavior_type","count"
"buy","2015839"
"cart","5530446"
"fav","2888258"
"pv","89716264"
"TOTAL","100150807"
从行为类型分布看，pv（页面浏览）占比超过 89%，buy（购买）仅占约 2%，cart 和 fav（加购、收藏）占比较小。符合电商平台典型的“转化漏斗”结构。

4. 判断用户行为次数的异常值
-- a. 统计每个用户的行为次数，存到临时表
CREATE TEMPORARY TABLE user_behavior_count AS 
SELECT user_id, COUNT(*) AS behavior_count
FROM taobao_behavior_original
GROUP BY user_id;

-- b. 获取总行数（样本量）
SELECT COUNT(*) FROM user_behavior_count;
-- 得到 987994 行

-- c. 给每一行加上排序编号，存成新的临时表
SET @row_index := 0;

CREATE TEMPORARY TABLE user_behavior_ranked AS
SELECT 
    user_id,
    behavior_count,
    @row_index := @row_index + 1 AS row_num
FROM user_behavior_count
ORDER BY behavior_count;

-- d. 计算 Q1 和 Q3，放入变量
SELECT 
  AVG(behavior_count) INTO @Q1
FROM user_behavior_ranked
WHERE row_num IN (FLOOR(987994 * 0.25), CEIL(987994 * 0.25));

SELECT 
  AVG(behavior_count) INTO @Q3
FROM user_behavior_ranked
WHERE row_num IN (FLOOR(987994 * 0.75), CEIL(987994 * 0.75));

-- e. 计算 IQR 和异常值上下界，存变量
SET @IQR = @Q3 - @Q1;
SET @lower_bound = @Q1 - 1.5 * @IQR;
SET @upper_bound = @Q3 + 1.5 * @IQR;

-- f. 查看计算结果（调试用）
SELECT @Q1 AS Q1, @Q3 AS Q3, @IQR AS IQR, @lower_bound AS lower_bound, @upper_bound AS upper_bound;

结果:
"Q1","Q3","IQR","lower_bound","upper_bound"
"39","136","97","-106.5","281.5"

-- g. 筛选行为次数大于上界的异常高频用户（刷量用户?）
SELECT user_id, behavior_count
FROM user_behavior_ranked
WHERE behavior_count > @upper_bound
ORDER BY behavior_count DESC;

为识别行为频率极高的异常用户（如刷量用户），使用 IQR 法对每位用户的行为记录数进行异常值检测：
共统计出 987,994 名用户的行为次数
采用中位数分位计算法，得出：
Q1 = 39
Q3 = 136
IQR = 97
Upper Bound = 281.5
根据上界筛选行为次数超过 281 的用户，识别为行为异常高频用户，共47720人，记录已保存于：
每个用户的行为次数存储位置:
data/processed/01_user_behavior_count
行为次数大于上界的异常高频用户存储位置:
data/processed/02_outlier_users_high


5. 时间范围确认
SELECT 
    MIN(FROM_UNIXTIME(ts)) AS min_time,
    MAX(FROM_UNIXTIME(ts)) AS max_time
FROM taobao_behavior_original;
结果显示
"min_time","max_time"
"1/1/1970 08:04:19","9/4/2037 13:22:35"
利用 FROM_UNIXTIME(ts) 将原始时间戳转换为可读格式，发现最早时间为 1970-01-01，最晚时间为 2037-09-04，显著超出官方说明的合理区间（2017-11-25 至 2017-12-03），说明数据中存在大量非法时间记录。应在数据清洗阶段删除。