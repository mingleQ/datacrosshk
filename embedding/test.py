import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 获取 API_ID
api_id = os.getenv('ZHIPU_API_ID')

# 打印 API_ID 以验证
print(f"API_ID: {api_id}")

# 你的其他代码
print(api_id)