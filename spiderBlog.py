# -*- coding: utf-8 -*-
# @Time: 2022/5/29 15:13
# @Author: pepsi-wyl
# @File: spiderBlog.py
# @Software: PyCharm


import os
import shutil
import requests
import re
from bs4 import BeautifulSoup
from lxml import etree
import csv
import sqlite3


# 文件初始化
def initFile():
    print("初始化文件的信息......")
    # HTML 存放路径初始化
    if os.path.exists('G:\\python\\yiqing\\HTML'):
        # 创建目录及其文件
        shutil.rmtree('G:\\python\\yiqing\\HTML')
        os.mkdir('G:\\python\\yiqing\\HTML')
    # CSV文件初始化
    if os.path.exists("G:\\python\\yiqing\\articleMsg.csv"):
        # 存在则删除文件
        os.remove("G:\\python\\yiqing\\articleMsg.csv")
    print("初始化文件的信息成功......")


# 开始爬取数据
def crawl():
    # 请求头信息
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.88 Safari/537.36 '
    }

    # 页面循环
    for i in range(1, 19, 1):

        if i == 1:
            url = "https://www.kingname.info/archives/"
        else:
            url = "https://www.kingname.info/archives/page/{}/".format(i)
        print("正在爬取第{}页的文章信息......URL为{}......".format(i, url))

        # 获取HTML数据
        html = getHTML(url, headers)

        # 获取当前页面所有表文章  标题、链接、发时间
        articleTitles, articleUrls, postTime = getFoundationMsgList(html)

        # 进入当前页面的每一篇文章，获取文章分类保存主要内容为html格式
        classify = []  # 分类
        getSeniorMsgList(headers, articleTitles, articleUrls, classify)

        # 将当前页面的信息写入csv
        saveToCsv(articleTitles, articleUrls, classify, postTime)

        # 将当前页面的信息保存到sqlite数据库中
        savaToSqlLite(articleTitles, articleUrls, classify, postTime)


# 获取页面信息  返回一个页面的HTML数据
def getHTML(url, headers):
    try:
        print("正在获取当前页面HTML......")
        r = requests.get(url, headers=headers)
        r.raise_for_status()  # 判断返回的是否为200
        r.encoding = r.apparent_encoding
        print("获取当前页面HTML成功......")
        return r.content
    except:
        return "error"


# 获取一个页面  返回一个页面文章的 标题、链接、发表时间
def getFoundationMsgList(html):
    print("正在获取当前页面所有表文章  标题、链接、发时间......")

    html = etree.HTML(html, parser=etree.HTMLParser(encoding='utf8'))

    # 获取文章标题  列表  文本使用text()
    articleTitles = html.xpath("/html/body/div/main/div/div[1]/div/div/div/article/header/h2/a/span/text()")
    print("获取当前页面文章标题成功......")

    # 获取文章链接  列表  链接使用@href
    selector = html.xpath("/html/body/div/main/div/div[1]/div/div/div/article/header/h2/a/@href")
    articleUrls = ['https://www.kingname.info/' + x for x in selector]
    print("获取当前页面文章链接成功......")

    # 获取文章发布时间 列表
    postTime = []
    for i in range(1, len(articleTitles) + 1, 1):
        time = html.xpath('normalize-space(//*[@id="posts"]/article[{}]/header/div/time/@datetime)'.format(i))
        postTime.append(time)
    print("获取当前页面文章发布时间成功......")

    return articleTitles, articleUrls, postTime


# 获取文章的分类和主要内容
def getSeniorMsgList(headers, articleTitles, articleUrls, classify):
    cnt = 1
    for url in articleUrls:
        print('正在爬取第{}篇文章的信息'.format(cnt))
        html = getHTML(url, headers)
        cnt += 1

        print("正在获取文章的分类信息和文章正文信息......")

        # 获取文章的分类信息
        cls = getArticleClass(html)
        lens = len(classify)
        classify[lens:lens] = cls
        print("获取文章的分类信息成功......")

        # 获取文章内容并保存为html
        getArticleBody(html, articleTitles[cnt - 2])


# 获取文章的分类
def getArticleClass(html):
    html = etree.HTML(html, parser=etree.HTMLParser(encoding='utf8'))
    cls = html.xpath(
        "/html/body/div/main/div/div[1]/div[1]/div/article/div/header/div/span[2]/span[4]/a/span/text()")
    if not cls:
        cls = ' '
    return cls


# 文件名称非法问题
def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


# 获取文章内容并保存为html
def getArticleBody(html0, articleTitle):
    # 模板
    html_template = """ 
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
    {content}
    </body>
    </html>
    """
    save_path = 'G:\\python\\yiqing\\HTML\\{}.html'.format(validateTitle(articleTitle))
    soup = BeautifulSoup(html0, 'html.parser')
    article = soup.select("p")  # 文章内容在p标签中
    article = str(article)

    article = article[1:len(article) - 1]
    article = article.replace(',', '')

    html = html_template.format(content=article)
    html = html.encode('utf-8')

    # 保存为html
    with open(save_path, 'wb') as f:
        f.write(html)
    print("获取文章的正文信息并且保存成功......")


# 保存到csv
def saveToCsv(articleTitles, articleUrls, classify, postTime):
    print("正在保存数据到CSV文件中......")
    with open(r"G:/python/yiqing/articleMsg.csv", 'a+', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(articleTitles)):
            writer.writerow([articleTitles[i], classify[i], postTime[i], articleUrls[i]])
    print("保存数据到CSV文件中成功......")


# 数据库工具类
def dbUtil(sql, dbPath):
    conn = sqlite3.connect(dbPath)  # 打开或者创建数据库文件
    conn.cursor().execute(sql)  # 获取游标  执行sql语句
    conn.commit()  # 提交数据库操作
    conn.close()  # 关闭数据库连接


# 初始化数据库
def initDatabases():
    print("正在初始化数据库中......")
    db = 'blogDatabases'
    # 表存在则删除
    sql = """
    drop table if exists blogMsg
    """
    print("表存在则删除" + sql)
    dbUtil(sql, db)
    # 创建表
    sql = """
    create table blogMsg(
    id integer primary key autoincrement,
    articleTitles varchar,
    classify varchar,
    postTime varchar,
    articleUrls varchar)
    """
    print("创建表" + sql)
    dbUtil(sql, db)
    print("初始化数据库成功......")


# 保持数据到SQLite中
def savaToSqlLite(articleTitles, articleUrls, classify, postTime):
    print("将数据插入到数据库中......")
    db = 'blogDatabases'
    for index in range(len(articleTitles)):
        sql = """
        insert into  blogMsg(articleTitles,classify,postTime,articleUrls) 
        values ('{}','{}','{}','{}')
        """.format(articleTitles[index], classify[index], postTime[index], articleUrls[index])
        print("插入数据" + sql)
        dbUtil(sql, db)
    print("数据插入到数据库中成功......")


# 执行
def main():
    # 初始化文件
    initFile()
    # 初始化数据库
    initDatabases()
    # 爬取信息和保存信息
    crawl()


if __name__ == "__main__":
    main()
