import os
import asyncio
from pyppeteer import launch
from pyquery import PyQuery as pq

import constant


async def login(browser, username, password):
    page = await browser.newPage()
    await page.goto(constant.LOGIN_URL)
    # 点击使用用户名密码
    await page.click('')
    # 等待加载出登录页面
    for i in range(20):
        if await page.querySelector('用户名密码'):
            break
        await page.waitFor(500)

    # 填写信息
    # 如果没有获取到，则会报PageError
    await page.type("#用户名id", username, {'delay': 100})
    await page.type("#密码", password, {'delay': 100})

    # 点击登录
    await page.click("")
    await page.waitFor(1000)
    # 判断是否登录成功


async def auto_scroll(page):
    # 网页可见高度
    total_height = 0

    # 网页全文高度
    scroll_height = await page.evaluate("document.body.scrollHeight")
    # 每次下拉100
    distance = 100

    while total_height < scroll_height:
        page.evaluate("window.scrollBy(0, {})".format(distance))
        total_height += distance
        scroll_height = await page.evaluate("document.body.scrollHeight")


async def get_all_subscribe_infos(browser):
    # 获取用户页面
    pages = await browser.pages()
    user_page = None
    for page in pages:
        if page.url == constant.USER_URL:
            user_page = page
            break

    # 下拉，获取所有订阅信息
    await auto_scroll(user_page)
    doc = pq(await user_page.content())

    # 抓取订阅信息
    doc('.quote')

    return []


async def get_column_article_infos(browser, column):
    """访问专栏详情页面"""
    page = await browser.newPage()
    url = constant.COLUMN_URL + column
    await page.goto(url)
    doc = pq(await page.content())

    # 抓取订阅信息
    doc('.quote')

    await page.close()
    return []


async def download_article_as_pdf(browser, article_name, article_id, path):
    """将文章保存为pdf"""
    page = await browser.newPage()
    url = constant.ARTICLE_URL + article_id
    await page.goto(url)
    file_name = article_name + '.pdf'
    file_path = os.path.join(path, file_name)
    await page.pdf(path=file_path)
    await page.close()


async def download_column_to_pdf(browser, column, path):
    article_infos = await get_column_article_infos(browser, column)
    for info in article_infos:
        await download_article_as_pdf(browser, info['artilce_title'], info['id'], path)


async def main():
    # 启动浏览器
    browser = await launch()
    username = ''
    password = ''
    path = ''
    # 登录
    await login(browser, username, password)

    # 获取所有订阅信息
    subscribe_infos = await get_all_subscribe_infos(browser)

    # 下载订阅的文章
    for info in subscribe_infos:
        await download_column_to_pdf(browser, info, path)


asyncio.get_event_loop().run_until_complete(main())
