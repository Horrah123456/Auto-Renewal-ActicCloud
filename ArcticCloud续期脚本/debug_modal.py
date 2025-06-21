import time
import json
import logging
import os
from datetime import datetime
from venv import logger

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def setup_logging():
    """配置日志记录，同时输出到控制台和文件"""
    # 确保 log 文件夹存在
    if not os.path.exists('log'):
        os.makedirs('log')

    # 生成带时间戳的日志文件名
    log_filename = datetime.now().strftime('renewal_log_%Y-%m-%d_%H-%M-%S.log')
    log_filepath = os.path.join('log', log_filename)

    # 创建 logger
    logger = logging.getLogger('RenewalBot')
    logger.setLevel(logging.INFO)

    # 创建文件处理器
    fh = logging.FileHandler(log_filepath, encoding='utf-8')
    fh.setLevel(logging.INFO)

    # 创建控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # 定义日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 添加处理器到 logger (避免重复添加)
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


def load_config():
    """从 config.json.example 加载配置"""
    try:
        with open('config.json.example', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("配置文件 config.json.example 未找到！")
        return None
    except json.JSONDecodeError:
        logger.error("配置文件 config.json.example 格式错误！")
        return None


def main():
    logger = setup_logging()
    config = load_config()
    if not config:
        return

    logger.info("调试模态框：开始执行...")
    driver = None
    try:
        # --- 登录与导航 ---
        logger.info("初始化并登录...")
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        driver.get("https://vps.polarbear.nyc.mn/index/login/")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "swapname"))).send_keys(config['username'])
        driver.find_element(By.NAME, "swappass").send_keys(config['password'])
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

        product_url = f"https://vps.polarbear.nyc.mn/control/detail/{config['product_id']}/"
        logger.info(f"导航到产品页: {product_url}")
        driver.get(product_url)

        logger.info("点击'续费产品'按钮以打开模态框...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '续费产品')]"))).click()
        time.sleep(2)  # 等待模态框动画

        # --- 核心侦察逻辑 ---
        logger.info("=" * 20 + " 模态框侦察开始 " + "=" * 20)

        # 1. 检查是否存在 iframe
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        if iframes:
            logger.warning(f"页面上发现了 {len(iframes)} 个 iframe！这可能是点击失败的原因。")
            for i, frame in enumerate(iframes):
                logger.info(f"  Iframe {i}: id='{frame.get_attribute('id')}', name='{frame.get_attribute('name')}'")
        else:
            logger.info("页面上未发现 iframe。")

        # 2. 尝试用多种方式定位“续期”按钮
        logger.info("尝试用不同策略定位'续期'提交按钮...")
        locators = {
            "XPath by value": "//input[@type='submit' and contains(@value, '续期')]",
            "XPath by class": "//input[contains(@class, 'install-complete')]",
            "CSS Selector by type and class": "input.install-complete[type='submit']"
        }

        found = False
        for name, locator in locators.items():
            try:
                # 使用 find_elements (复数) 来查找，这样找不到时不会报错，而是返回空列表
                button = driver.find_elements(By.XPATH, locator) if "XPath" in name else driver.find_elements(
                    By.CSS_SELECTOR, locator)
                if button:
                    logger.info(f"  [成功] 使用 '{name}' 策略找到了按钮。")
                    found = True
                else:
                    logger.warning(f"  [失败] 使用 '{name}' 策略未找到按钮。")
            except Exception as e:
                logger.error(f"  [错误] 使用 '{name}' 策略时发生异常: {e}")

        if not found:
            logger.error("所有策略均未能定位到'续期'按钮！")

        logger.info("=" * 20 + " 侦察结束 " + "=" * 20)
        logger.info("脚本将暂停10秒以便观察，然后关闭。")
        time.sleep(10)

    except Exception as e:
        logger.error(f"在执行过程中发生了严重错误: {e}", exc_info=True)
        time.sleep(10)

    finally:
        if driver:
            driver.quit()
        logger.info("调试脚本执行完毕。")


if __name__ == "__main__":
    main()