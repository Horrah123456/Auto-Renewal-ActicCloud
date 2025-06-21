import time
import json
import logging
import os
import requests
import sys
import base64
from datetime import datetime
import pytz

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 【最终版】我们使用这个简单可靠的混淆密钥
ENCODED_MASTER_KEY = "QmVhckJvc3NfSXNfV2F0Y2hpbmdfWW91X1hIRw=="


def setup_logging():
    if not os.path.exists('log'):
        os.makedirs('log')
    log_filename = datetime.now().strftime('renewal_log_%Y-%m-%d_%H-%M-%S.log')
    log_filepath = os.path.join('log', log_filename)
    logger = logging.getLogger('RenewalBot')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    if not logger.handlers:
        fh = logging.FileHandler(log_filepath, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger


def load_config():
    config = {}
    try:
        config['username'] = os.environ['USERNAME']
        config['password'] = os.environ['PASSWORD']
        config['product_id'] = os.environ['PRODUCT_ID']
        config['bot_token'] = os.environ['BOT_TOKEN']
        config['chat_id'] = os.environ['CHAT_ID']
        config['script_secret_key'] = os.environ.get('SCRIPT_SECRET_KEY')
        logging.info("从环境变量中加载配置成功。")
    except KeyError:
        logging.info("未找到核心环境变量，尝试从 config.json.example 加载配置。")
        try:
            with open('config.json.example', 'r') as f:
                config = json.load(f)
                logging.info("从 config.json.example 加载配置成功。")
        except FileNotFoundError:
            logging.error("未找到环境变量，也未找到 config.json.example 文件！")
            return None
    return config


def send_telegram_message(token, chat_id, text):
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'MarkdownV2'}
    try:
        requests.post(api_url, data=payload, timeout=10)
        logging.info("Telegram 通知已发送。")
    except Exception as e:
        logging.error(f"发送 Telegram 通知失败: {e}")


def get_expiry_date(driver):
    try:
        list_item_xpath = "//li[contains(text(), '到期时间')]"
        list_item = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, list_item_xpath)))
        full_text = list_item.text
        parts = full_text.split(' ')
        date_index = parts.index('到期时间') + 1
        return parts[date_index]
    except Exception:
        logging.error("提取到期时间失败。", exc_info=True)
        return None


def get_master_key():
    try:
        b64_string = ENCODED_MASTER_KEY
        decoded_bytes = base64.b64decode(b64_string)
        return decoded_bytes.decode('utf-8')
    except Exception:
        return ""


def main():
    logger = setup_logging()
    config = load_config()
    if not config:
        return

    # 为了避免出现骑脸行为导致加入反自动策略故采取此措施，见谅！
    user_provided_key = config.get('script_secret_key')

    master_key = get_master_key()

    if user_provided_key != master_key:
        error_message = "该版本已经失效！如有需要请联系：https://t.me/XHGchat_bot😄"
        logger.error(f"密钥验证失败！{error_message}")
        sys.exit()

    logger.info("密钥验证成功，准许执行。")

    bot_token = config.get('bot_token')
    chat_id = config.get('chat_id')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # 【修改】记录开始时间并发送启动通知
    start_time = time.monotonic()
    start_time_str = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
    start_message = f"🚀 *ArcticCloud续期任务开始执行* 🚀\n\n*开始时间:* `{start_time_str}`"
    send_telegram_message(bot_token, chat_id, start_message)

    logger.info("=" * 10 + " 自动续期任务启动 " + "=" * 10)
    driver = None
    try:
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
        before_date_str = get_expiry_date(driver)
        if not before_date_str:
            raise Exception("无法获取初始到期时间，脚本终止。")
        logger.info(f"操作前，到期时间为: {before_date_str}")
        current_time = datetime.now(beijing_tz).date()
        expiry_time = datetime.strptime(before_date_str, '%Y-%m-%d').date()
        days_left = (expiry_time - current_time).days
        is_already_safe = days_left >= 5
        logger.info(f"当前北京日期: {current_time}, 剩余天数: {days_left}天。")
        if is_already_safe:
            logger.info("到期时间充裕 (>=5天)，本次操作为健康检查或重复执行。")
        logger.info("点击'续费产品'按钮...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '续费产品')]"))).click()
        logger.info("点击最终的'续期'提交按钮...")
        submit_button_xpath = "//input[contains(@class, 'install-complete')]"
        wait.until(EC.element_to_be_clickable((By.XPATH, submit_button_xpath))).click()
        logger.info("提交操作已执行！等待页面刷新数据...")
        time.sleep(5)
        driver.refresh()
        logger.info("重新获取到期时间以进行验证...")
        after_date_str = get_expiry_date(driver)
        if not after_date_str:
            raise Exception("无法获取续期后的到期时间，请手动检查。")
        logger.info(f"操作后，到期时间为: {after_date_str}")
        logger.info("=" * 10 + " 任务结果报告 " + "=" * 10)
        final_report = ""
        if before_date_str != after_date_str:
            logger.info(f"🎉 续费成功！到期时间已从【{before_date_str}】更新为【{after_date_str}】。")
            final_report = (f"🎉 *续费成功* 🎉\n\n"
                            f"产品ID: `{config['product_id']}`\n"
                            f"到期时间已从 `{before_date_str}` 更新为 *`{after_date_str}`*")
        else:
            if is_already_safe:
                logger.info(f"✅ 例行检查完成。到期时间充裕，保持在【{before_date_str}】未发生变化。")
                final_report = (f"✅ *例行检查完成* ✅\n\n"
                                f"产品ID: `{config['product_id']}`\n"
                                f"到期时间为 `{before_date_str}`，无需续期。")
            else:
                logger.warning(f"⚠️ 续费失败！到期时间保持在【{before_date_str}】未发生变化。请关注！")
                final_report = (f"⚠️ *续费失败* ⚠️\n\n"
                                f"产品ID: `{config['product_id']}`\n"
                                f"尝试续期，但到期时间未能更新，仍为 `{before_date_str}`")

        # 【修改】加入任务耗时信息
        end_time = time.monotonic()
        end_time_str = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        duration = round(end_time - start_time)
        timing_info = f"\n\n*结束时间:* `{end_time_str}`\n*总耗时:* `{duration} 秒`"

        final_report += timing_info
        final_report += "\n\n`我要告诉熊老板你开挂！--by  XHG`"
        send_telegram_message(bot_token, chat_id, final_report)
        time.sleep(10)

    except Exception as e:
        logger.error(f"在执行过程中发生了严重错误。", exc_info=True)
        # 【修改】错误报告也加入时间信息
        end_time = time.monotonic()
        end_time_str = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        duration = round(end_time - start_time)
        timing_info = f"\n\n*发生时间:* `{end_time_str}`\n*已运行:* `{duration} 秒`"

        error_report = (f"❌ *任务执行失败* ❌\n\n"
                        f"产品ID: `{config['product_id']}`\n"
                        f"错误信息: `{e}`\n\n"
                        f"`请检查日志获取详细信息`")
        error_report += timing_info
        error_report += "\n\n`我要告诉熊老板你开挂！--by  XHG`"
        send_telegram_message(bot_token, chat_id, error_report)
        time.sleep(10)

    finally:
        if driver:
            driver.quit()
        logger.info("=" * 10 + " 自动续期任务结束 " + "=" * 10)


if __name__ == "__main__":
    main()
