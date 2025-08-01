1. 字段预览
原始数据表 taobao_behavior 包含以下字段：
| 字段名             | 类型      | 说明                      |
| --------------- | ------- | ----------------------- |
| `user_id`       | BIGINT  | 用户唯一标识                  |
| `item_id`       | BIGINT  | 商品唯一标识                  |
| `category_id`   | BIGINT  | 商品所属类目 ID               |
| `behavior_type` | VARCHAR | 用户行为类型（pv/buy/cart/fav） |
| `ts`            | BIGINT  | 行为发生时间（Unix 时间戳）        |

注意:
字段命名在导入阶段就是英文
字段类型初步设定为 BIGINT 和 VARCHAR，在结构优化阶段可能会调整；
字段 ts 后续将通过 FROM_UNIXTIME(ts) 转换为可读时间 event_time
2. 数据总量
共100,150,807条记录

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

4. 判断用户行为次数的异常值

-- 1. 统计每个用户的行为次数，存到临时表
CREATE TEMPORARY TABLE user_behavior_count AS 
SELECT user_id, COUNT(*) AS behavior_count
FROM taobao_behavior_original
GROUP BY user_id;

-- 2. 获取总行数（样本量）
SELECT COUNT(*) FROM user_behavior_count;
-- 得到 987994 行

-- 3. 给每一行加上排序编号，存成新的临时表
SET @row_index := 0;

CREATE TEMPORARY TABLE user_behavior_ranked AS
SELECT 
    user_id,
    behavior_count,
    @row_index := @row_index + 1 AS row_num
FROM user_behavior_count
ORDER BY behavior_count;

-- 计算 Q1 和 Q3，放入变量
SELECT 
  AVG(behavior_count) INTO @Q1
FROM user_behavior_ranked
WHERE row_num IN (FLOOR(987994 * 0.25), CEIL(987994 * 0.25));

SELECT 
  AVG(behavior_count) INTO @Q3
FROM user_behavior_ranked
WHERE row_num IN (FLOOR(987994 * 0.75), CEIL(987994 * 0.75));

-- 计算 IQR 和异常值上下界，存变量
SET @IQR = @Q3 - @Q1;
SET @lower_bound = @Q1 - 1.5 * @IQR;
SET @upper_bound = @Q3 + 1.5 * @IQR;

-- 查看计算结果（调试用）
SELECT @Q1 AS Q1, @Q3 AS Q3, @IQR AS IQR, @lower_bound AS lower_bound, @upper_bound AS upper_bound;

结果:
"Q1","Q3","IQR","lower_bound","upper_bound"
"39","136","97","-106.5","281.5"

-- 筛选行为次数大于上界的异常高频用户（刷量用户?）
SELECT user_id, behavior_count
FROM user_behavior_ranked
WHERE behavior_count > @upper_bound
ORDER BY behavior_count DESC;

-- lower_bound 是负值, 不存在行为次数小于下界的异常低频用户


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
说明数据存在大量不属于范围内的值,应在数据清洗阶段进行清洗