import pandas as pd
import mysql.connector
from tqdm import tqdm
import traceback
import time

# ✅ 设置 CSV 路径
csv_file = '/Users/wuzeyu/qi/data_analysis_projects/project_1_taobao_behavior/data/raw/raw_user_behavior.csv'

# ✅ 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'taobao_behavior',
    'auth_plugin': 'mysql_native_password'
}

# ✅ 表信息
table_name = 'taobao_behavior'
columns = ['user_id', 'item_id', 'category_id', 'behavior_type', 'ts']
start_row = 0
batch_size = 10000

# ✅ 记录开始时间
start_time = time.time()

try:
    # ✅ 计算总行数（用于 tqdm 进度条）
    with open(csv_file, 'r') as f:
        total_rows = sum(1 for _ in f)

    # ✅ 建立数据库连接
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # ✅ SQL 插入语句
    sql = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """

    # ✅ 分批读取并导入数据
    reader = pd.read_csv(
        csv_file,
        header=None,
        names=columns,
        chunksize=batch_size,
        skiprows=range(1, start_row + 1)
    )

    print("📦 开始导入数据中，请稍候...")
    for i, chunk in enumerate(tqdm(reader, total=(total_rows - start_row) // batch_size)):
        data = chunk.values.tolist()
        cursor.executemany(sql, data)
        conn.commit()

    print(f"✅ 数据导入完成！总耗时 {(time.time() - start_time)/60:.2f} 分钟")

except Exception as e:
    print("❌ 出现错误：", e)
    traceback.print_exc()

finally:
    # ✅ 关闭连接
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
