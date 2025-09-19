# 🎯 淘宝用户购物行为数据分析项目

> 本项目基于阿里巴巴天池平台开放的淘宝用户行为数据，分析用户在电商平台中的典型行为路径，识别高价值用户、潜力商品和转化瓶颈，最终为平台的运营优化和策略决策提供支持。

---

## 🧠 项目背景

- **数据来源**：[阿里云天池](https://tianchi.aliyun.com/dataset/649)
- **时间范围**：2017-11-25 至 2017-12-03（共9天）
- **数据体量**：约 1 亿条行为记录，约100 万用户

---

## 🛠️ 技术栈与工具

- **数据库管理**：MySQL 8.0（Navicat / DataGrip 辅助）
- **数据处理**：SQL 脚本（分阶段执行）
- **可视化**：Tableau Public
- **版本管理**：Git + GitHub
- **文档撰写**：Markdown（报告、README）

---

## 📊 项目结构

```bash
project_1_taobao_behavior/
.
├── README.md                         # 项目说明文件
├── data                              # 数据存放目录
│   ├── raw                           # 原始数据
│   └── processed                     # 中间数据
│
├── docs                              # 分析文档
│   ├── analysis                      # 分析过程
│   └── report                        # 项目报告
│
├── output                            # 输出结果
│   └── images                        # 可视化图表
│
└── src                               # 源代码
    ├── python                        # Python 脚本
    └── sql                           # SQL 脚本
