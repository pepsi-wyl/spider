import sqlite3
import spiderBlog
from flask import Flask, render_template, redirect, request

app = Flask(__name__)


# 首页信息
@app.route('/')
@app.route('/index')
def index():
    conn = sqlite3.connect("blogDatabases")
    # 博客数量
    for itemBlog in conn.cursor().execute("select count(*)  from blogMsg"):
        print(itemBlog[0])
    # 博客分类
    for itemClassify in conn.cursor().execute("select count(distinct classify) from  blogMsg"):
        print(itemClassify[0])
    # 关闭连接
    conn.close()
    return render_template("index.html", blogCount=itemBlog[0], classifyCount=itemClassify[0])


# 博客详情信息
@app.route('/blog')
def blog():
    dataList = []
    conn = sqlite3.connect("blogDatabases")
    # 获取所有博客信息
    for itemBlog in conn.cursor().execute("select * from blogMsg"):
        dataList.append(itemBlog)
    # 关闭连接
    conn.close()
    return render_template("blog.html", dataList=dataList)


# 博客信息分析
@app.route('/fenxi')
def fenxi():
    conn = sqlite3.connect("blogDatabases")
    # 获取所有的分类种类
    classify = []
    for itemClassify in conn.cursor().execute("select distinct classify from  blogMsg"):
        pass
        classify.append(itemClassify[0])
    print(classify)
    # 获取所有的分类数量
    classifyCount = []
    for item in classify:
        sql = "select count(*) from blogMsg where classify='{}'".format(item)
        for itemClassifyCount in conn.cursor().execute(sql):
            classifyCount.append(itemClassifyCount[0])
    print(classifyCount)
    return render_template("fengxi.html", classify=classify, classifyCount=classifyCount)


# 管理员重新爬取数据
@app.route('/admin')
def admin():
    return render_template("admin.html", title="登录")  # 渲染模板


# 管理员爬取数据验证条件
@app.route('/toLogin', methods=['POST', 'GET'])
def toLogin():
    result = request.form
    if result['username'] == 'pepsi-wyl' and result['password'] == '888888':
        spiderBlog.main()
    else:
        print("error")
    return redirect('/index', code=302, Response=None)


if __name__ == '__main__':
    app.run()
