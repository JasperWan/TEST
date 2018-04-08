import re
import requests
from requests.exceptions import RequestException
from config import *
import pymongo

# 声明mongodb对象
client = pymongo.MongoClient(MONGO_URL)
# 数据库名称
db = client[MONGO_DB]

def get_page_index(url,headers):
    """请求索引页"""
    try:
        # 发送请求，获取响应
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        # 获取失败，返回None
        return None
    except RequestException:
        return None


def parse_page_index(html):
    """解析索引页"""
    # 正则匹配
    pattern = re.compile('<dd>.*?board-index.*?>(\d+).*?<a href="(.*?)" title="(.*?)" class.*?<img src="(.*?)".*?board-item-main".*?<p.*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">(.*?)<.*?fraction">(.*?)</i>.*?</dd>',re.S)
    results = re.findall(pattern,html)
    for item in results:
        yield {
            'ranking':item[0],  # 排名
            'detail_url':item[1],  # 详情页后缀
            'title':item[2],  # 标题
            'actor':item[4].strip()[3:],  # 主演
            'time':item[5][5:],  # 上映时间
            'score':item[6]+item[7],  # 评分
            'img_url':item[3],  # 图片地址
        }

def save_to_mongo(result):
    """存储到mongo"""
    if db[MONGO_TABLE].insert(result):
        print('存储mongo成功')
        return True
    return False



def main(offset):
    url = "http://maoyan.com/board/4?offset=" + str(offset)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"}
    html = get_page_index(url,headers)
    # 获取每一条结果
    for item in parse_page_index(html):
        print(item)
        # 存储mongo
        save_to_mongo(item)



if __name__ == '__main__':
    # 请求多页
    for i in range(10):
        main(i*10)