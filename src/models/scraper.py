"""
WebScraper类 - 一个简单的网页爬取器

类方法：
    __init__(self, scraper_type='requests', proxy=None, headless=False) - 初始化WebScraper对象
    fetch_page(self, url) - 获取页面内容
    post_page(self, url, post_headers=None, data_post=None) - 发送POST请求
    close(self) - 关闭WebScraper对象，释放资源
    user_agent_header - 获取用户代理请求头

类属性：
    user_agent_header - 获取用户代理请求头

类示例：


"""

# 标准库导入
import time
import random
from threading import Thread
# 相关第三方导入
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
# 本地导入
from .logger import log_decorator

class Scraper:
    @log_decorator
    def __init__(self, scraper_type='requests', proxy=None, headless=False):
        """
        初始化WebScraper对象

        Args:
            scraper_type (str, optional): 爬取类型，可选值为'requests'或'selenium'，默认为'requests'
            proxy (str, optional): 代理服务器地址，如果提供，则使用代理服务器进行请求
            headless (bool, optional): 是否启用无头模式，如果为True，则隐藏浏览器窗口，默认为False
        """
        self.max_retries = 3
        self.retry_delay = (1, 3)
        self.scraper_type = scraper_type
        self.user_agent = self._random_user_agent()
        self.proxy = proxy
        if scraper_type == 'selenium':
            # 设置代理（如果提供）
            chrome_options = webdriver.ChromeOptions()
            if proxy:
                chrome_options.add_argument(f'--proxy-server={proxy}')
            if headless:
                chrome_options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            self.driver = None

    # 随机user_agent方法，不同浏览器，不同操作系统
    def _random_user_agent(self):
        """
        随机生成用户代理

        Returns:
            str: 用户代理字符串
        """
        # 随机选择操作系统
        os = random.choice(['Macintosh', 'Windows', 'X11'])
        if os == 'Macintosh':
            # 随机选择Macintosh操作系统
            os_version = random.choice(['10_14_6', '10_15_7'])
            # 随机选择浏览器
            browser = random.choice(['Chrome', 'Firefox', 'Safari'])
            if browser == 'Chrome':
                # 随机选择Chrome浏览器版本
                browser_version = random.choice(['83.0.4103.97', '84.0.4147.105'])
            elif browser == 'Firefox':
                # 随机选择Firefox浏览器版本
                browser_version = random.choice(['77.0', '78.0'])
            else:
                # 随机选择Safari浏览器版本
                browser_version = random.choice(['13.1.1', '14.0'])
        elif os == 'Windows':
            # 随机选择Windows操作系统
            os_version = random.choice(['NT 6.1', 'NT 6.2', 'NT 6.3', 'NT 10.0'])
            # 随机选择浏览器
            browser = random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])
            if browser == 'Chrome':
                # 随机选择Chrome浏览器版本
                browser_version = random.choice(['83.0.4103.97', '84.0.4147.105'])
            elif browser == 'Firefox':
                # 随机选择Firefox浏览器版本
                browser_version = random.choice(['77.0', '78.0'])
            elif browser == 'Edge':
                # 随机选择Edge浏览器版本
                browser_version = random.choice(['83.0.478.61', '84.0.522.40'])
            else:
                # 随机选择Safari浏览器版本
                browser_version = random.choice(['5.0', '5.1'])
        else:
            # 随机选择Linux操作系统
            os_version = random.choice(['Ubuntu; Linux x86_64', 'X11; Linux x86_64'])
            # 随机选择浏览器
            browser = random.choice(['Chrome', 'Firefox'])
            if browser == 'Chrome':
                # 随机选择Chrome浏览器版本
                browser_version = random.choice(['83.0.4103.97', '84.0.4147.105'])
            else:
                # 随机选择Firefox浏览器版本
                browser_version = random.choice(['77.0', '78.0'])
        # 生成并返回用户代理字符串
        return f'Mozilla/5.0 ({os}; {os_version}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36'
    
    @log_decorator
    def fetch_page(self, url):
        """
        获取页面内容

        Args:
            url (str): 页面URL

        Returns:
            bytes or str: 页面内容，如果获取失败，则返回None
        """
        if self.scraper_type == 'requests':
            proxies = {'http': self.proxy, 'https': self.proxy} if self.proxy else None
            for retry in range(self.max_retries):
                try:
                    request_headers = {'User-Agent': self.user_agent}
                    response = requests.get(url, headers=request_headers, proxies=proxies, timeout=10)
                    if response.content:
                        time.sleep(random.uniform(*self.retry_delay))
                        return BeautifulSoup(response.content, 'html.parser')
                except requests.exceptions.RequestException:
                    if retry >= self.max_retries - 1:
                        return None
                    time.sleep(random.uniform(*self.retry_delay) * 10)
        elif self.scraper_type == 'selenium' and self.driver:
            for retry in range(self.max_retries):
                try:
                    self.driver.get(url)
                    if self.driver.page_source:
                        time.sleep(random.uniform(*self.retry_delay))
                        return BeautifulSoup(self.driver.page_source, 'html.parser')
                except Exception:  # 应该捕获更具体的异常
                    if retry >= self.max_retries - 1:
                        return None
                    time.sleep(random.uniform(*self.retry_delay))
        return None

    @log_decorator
    def post_page(self, url, post_headers=None, data_post=None):
        """
        发送POST请求

        Args:
            url (str): 请求URL
            post_headers (dict, optional): 请求头，如果提供，则会与默认请求头合并
            data_post (dict, optional): 请求数据，以JSON格式发送

        Returns:
            bytes or str: 响应内容，如果请求失败，则返回None
        """
        if self.scraper_type != 'requests':
            raise NotImplementedError("POST requests are only supported with the 'requests' scraper type.")
        for retry in range(self.max_retries):
            try:
                # full_headers = self.user_agent_header
                # if headers:
                #     full_headers = headers
                response = requests.post(url, headers=post_headers, json=data_post, timeout=10)
                response.raise_for_status()
                # time.sleep(random.uniform(*retry_delay))
                return response
            except requests.exceptions.RequestException:
                if retry >= self.max_retries - 1:
                    return None
                time.sleep(random.uniform(*self.retry_delay) * 10)

    @property
    def user_agent_header(self):
        """
        获取用户代理请求头

        Returns:
            dict: 请求头字典
        """
        return {'User-Agent': self.user_agent}

    def close(self):
        """
        关闭WebScraper对象，释放资源
        """
        if self.driver:
            self.driver.quit()

    def __del__(self):
        self.close()

def worker(spraper):
    print(spraper.fetch_page("https://www.baidu.com"))

if __name__ == "__main__":
    # webscraper = Scraper()
    # # r = webscraper.fetch_page("https://cx.cnnbfdc.com/agency/DetailsHistoryContract?pageIndex=1")
    # # print(r)
    # headers = {'X-ClientId': 'dev-id-1'}
    # data = {"url": "https://gateway.cnnbfdc.com/zjw/statistics/esf/last_month/district/agent_sold"}
    # r = webscraper.post_page("http://fwxx.zjw.ningbo.gov.cn/api/cnnbfdc/data", headers, data)
    # print(r.json())

    scraper1 = Scraper('selenium', headless=True)
    scraper2 = Scraper('selenium', headless=True)
    
    thread1 = Thread(target=worker, args=(scraper1,))
    thread2 = Thread(target=worker, args=(scraper2,))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    scraper1.close()
    scraper2.close()
    print("done")
    