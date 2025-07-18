-- ===================================================
-- 文件名：01_create_sample_db_database.sql
-- 功能：创建数据库 taobao_behavior_sample，设定编码格式
-- 作者：qiyulu
-- 日期：2025-07-13
-- ===================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS taobao_behavior_sample
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

-- 使用数据库
USE taobao_behavior_sample;

-- 创建表
CREATE TABLE IF NOT EXISTS taobao_behavior_sample (
user_id BIGINT,
item_id BIGINT,
category_id BIGINT,
hehavior_type VARCHAR(10),
ts BIGINT
);