import time
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from thu_learn_downloader.client import url


def login_with_browser() -> dict[str, Any]:
    """通过浏览器进行统一用户登录，返回登录后的cookies

    Returns:
        Dict[str, Any]: 包含登录后cookies的字典

    Raises:
        Exception: 当登录失败或浏览器操作失败时抛出异常
    """
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        # 初始化WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()

        # 访问登录页面
        login_url = url.make_url()
        print(f"正在打开登录页面: {login_url}")
        driver.get(login_url)

        # 等待页面加载
        wait = WebDriverWait(driver, 30)

        # 检查是否已经重定向到统一身份认证页面
        print("等待用户完成登录...")
        print("请在浏览器中输入您的用户名和密码完成登录")

        # 等待用户登录完成，监控URL变化
        # 通常登录成功后会重定向到课程页面或其他页面
        success_indicators = [
            "/f/wlxt/index/course/student/",
            "/b/wlxt/kc/",
            "course/student",
        ]

        # 轮询检查登录状态，最多等待5分钟
        timeout = 300  # 5分钟
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_url = driver.current_url

            # 检查是否登录成功
            if any(indicator in current_url for indicator in success_indicators):
                print("检测到登录成功！")
                break

            # 检查是否有特定的成功元素出现
            try:
                # 尝试查找登录成功后的特征元素
                driver.find_element(By.PARTIAL_LINK_TEXT, "课程")
                print("检测到课程页面，登录成功！")
                break
            except:
                pass

            time.sleep(2)  # 等待2秒后再次检查
        else:
            raise TimeoutException("登录超时，请重试")

        # 获取所有cookies
        cookies = driver.get_cookies()
        print(f"成功获取到 {len(cookies)} 个cookies")

        # 将cookies转换为requests库可用的格式
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]

        return cookie_dict

    except WebDriverException as e:
        raise Exception(f"浏览器操作失败: {e!s}")
    except Exception as e:
        raise Exception(f"登录过程中出现错误: {e!s}")
    finally:
        if driver:
            driver.quit()
