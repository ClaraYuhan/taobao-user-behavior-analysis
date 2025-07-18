-- ===================================================
-- 文件名：03_create_full_db_table.sql
-- 功能：创建数据库 taobao_behavior，创建表taobao_behavior
-- 作者：qiyulu
-- 日期：2025-07-16
-- ===================================================

-- 创建正式数据库
CREATE DATABASE IF NOT EXISTS taobao_behavior
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

-- 切换到正式数据库
USE DATABASE taobao_behavior;

-- 创建正式数据表
CREATE TABLE IF NOT EXISTS taobao_behavior(
user_id BIGINT,
item_id BIGINT,
category_id BIGINT,
behavior_type VARCHAR(10),
ts BIGINT
);
