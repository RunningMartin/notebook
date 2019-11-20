# pyppeteer使用笔记

## 安装

- 需要安装python 3.6+.
- `python3 -m pip install pyppeteer`
- 安装所需浏览器，避免第一次运行时安装：`pyppeteer-instal`

## 使用

pyppeteer内部采用协程实现，因此需要外部也需要使用协程。

```python
import asyncio
from pyppeteer import launch
width,height=1366,768
async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://www.baidu.com')
    await page.setViewport({'width':width,'height':height})
    await page.type("#kw",'python')
    await page.click("#submit")
    await page.screenshot({'path': 'example.png'})
    await page.pdf({'path': 'example.pdf'})

    dimensions = await page.evaluate('''() => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }''')
    print(dimensions)
    # >>> {'width': 800, 'height': 600, 'deviceScaleFactor': 1}
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())
```

- 启动浏览器：`browser = await launch()`
  - `headless`：是否采用无界面模式，默认为`False`。
  - `devtools`：是否为每个页面开启调试工具，默认为`False`。
  - `userDataDir`：用户数据文件存放位置，可以用于存放cookie。
  - `args`：添加Chrome的配置，为list。
    - `--disable-infobars`：关闭`Chrome正受到自动软件测试的控制`提示。
    - `--window-size={width},{height}`：设置浏览器窗口大小。
- 打开标签页：`page=await browser.newPage()`
- 跳转到相应页面：`await page.goto('https://www.baidu.com')`
- 设置页面大小：`await page.setViewport({'width':width,'height':height})`
- 截屏：`await page.screenshot({'path': 'example.png'})`
- 填写信息：`await page.type("#kw",'python')`
- 点击按钮：`await page.click("#submit")`
- 页面保存为pdf：`await page.pdf({'path': 'example.pdf'})`
- 执行JavaScript：`await page.evaluate()`

淘宝主要通过`window.navigator.webdriver`来对webdriver进行检测。

```javascript
() =>{
    Object.defineProperties(navigator,{
        webdriver:{
            get:() => false}
        }
    })   
}
```
