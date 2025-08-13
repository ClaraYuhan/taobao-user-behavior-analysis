import pandas as pd
import mysql.connector
from tqdm import tqdm
import time
import traceback

# ========== ✅ 基本配置 ==========
csv_file = '/Users/wuzeyu/qi/data_analysis_projects/project_1_taobao_behavior/data/raw/raw_user_behavior.csv'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'taobao_behavior',
    'auth_plugin': 'mysql_native_password'
}

table_name = 'taobao_behavior'
columns = ['user_id', 'item_id', 'category_id', 'behavior_type', 'ts']

start_row = 0
batch_size = 10000
max_rows = 100000  # ✅ 只导入前 10 万行

# ========== 🧠 SQL 语句 ==========
insert_sql = f"""
    INSERT INTO {table_name} ({', '.join(columns)})
    VALUES ({', '.join(['%s'] * len(columns))})
"""

truncate_sql = f"TRUNCATE TABLE {table_name}"


# ========== 🚀 执行导入流程 ==========
try:
    start_time = time.time()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 🧹 清空原始表
    print("🧹 正在清空数据表...")
    cursor.execute(truncate_sql)
    conn.commit()
    print("✅ 数据表已清空")

    # 🔢 计算总行数
    with open(csv_file, 'r') as f:
        total_rows = sum(1 for _ in f)

    reader = pd.read_csv(
        csv_file,
        header=None,
        names=columns,
        chunksize=batch_size,
        skiprows=range(1, start_row + 1)
    )

    print("📦 开始导入测试数据中（前 10 万行）...")
    rows_inserted = 0
    for chunk in tqdm(reader, total=min((max_rows - start_row) // batch_size, total_rows // batch_size)):
        if rows_inserted >= max_rows:
            break
        data = chunk.values.tolist()
        cursor.executemany(insert_sql, data)
        conn.commit()
        rows_inserted += len(data)

    print(f"✅ 测试导入完成，共导入 {rows_inserted:,} 行数据，用时 {(time.time() - start_time)/60:.2f} 分钟")

except Exception as e:
    print("❌ 出现错误：", e)
    traceback.print_exc()

finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()