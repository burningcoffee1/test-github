"""
This module contains code for extracting data from the city of Beijing.
"""
from ..scraper import Scraper

# 导入统一目录中的test.py模块
from . import test


# 创建Scraper对象
scraper = Scraper()
soup = scraper.fetch_page('http://bjjs.zjw.beijing.gov.cn/eportal/ui?pageId=307749')

# 提取表格
table_rows = soup.find_all('tr', bgcolor="#F9F4E8")

data = {}

# 遍历表格中的每一行，提取数据
for row in table_rows:
    cells = row.find_all('td')
    if len(cells) >= 2:  # 确保 cells 至少有两个元素
        key = cells[0].text.strip()
        value = cells[1].text.strip()
        data[key] = value
    else:
        print("找到的列数少于预期，跳过这一行")

for key, value in data.items():
    print(f"{key}: {value}")
    