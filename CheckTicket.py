from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options  # 引入無頭模式配置
from datetime import datetime
import time
import threading
import requests  # 用於發送 LINE Messaging API
from datetime import datetime

# 群組 ID（填入你的群組 ID）
LINE_GROUP_ID = 'C2aa60e1da3d316f6e97a431735aa596b'
# LINE Messaging API 的 Channel Access Token
LINE_CHANNEL_ACCESS_TOKEN = 'zSO7P2pG9HwpXV7B69AFVfsybr7qdFNDqjt24z93t/4W2N89zWnclv1/U5HF6Nu5eVKfLgyA69A9pvByfjN3XkHLoPjLvW8LpQyggcMNe8Prngvnuu8F9CzqijBxJVAu5968vYOQZaELYgLL2xW9eAdB04t89/1O/w1cDnyilFU='

# 發送訊息到 LINE 群組的函數
def send_line_message(to, messages):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": LINE_GROUP_ID,
        "messages": [
            {"type": "text", "text": messages}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("LINE 訊息發送成功")
    else:
        print(f"LINE 訊息發送失敗，狀態碼：{response.status_code}, 錯誤訊息：{response.text}")

# 查找並刷新頁面直到找到 '立即購買' 按鈕的函式
def check_buy_button(url, label, LINE_GROUP_ID):
    # 設置無頭模式
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 啟用無頭模式
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU，增加穩定性
    chrome_options.add_argument("--no-sandbox")  # 避免沙箱問題
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(5)
    #上次找到的時間
    last_found_time = 0
    #每張票買到約有十五分鐘(900s)的購買時間
    cooldown = 900  

    # 持續刷新直到找到"立即購買"按鈕
    while True:
        try:
            # 獲取當前日期和時間
            current_time = datetime.now()


            check_interval = 3


            # 格式化日期
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if "kktix.com" in url:
                try:
                    # 查找票務區域是否存在
                    # 檢查是否存在 .ticket-quantity.ng-scope 的 span 元素
                    elements = driver.find_elements(By.CSS_SELECTOR, ".display-table-row span.ticket-quantity.ng-binding.ng-scope")
                    found = False
                    for element in elements:
                        if "已售完" in element.text:
                            print(f"{formatted_time}-{label}--沒找到票，繼續刷新...")
                        else:
                            now = time.time()
                            current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            if now - last_found_time >= cooldown:
                                    message = f"{label}\n{formatted_time}\n目前有清票 🎉\n購買網址: \n{url}"
                                    print(message)
                                    # 發送到 LINE
                                    send_line_message(
                                    to=LINE_GROUP_ID,
                                    messages=message
                                    )  
                                     # 更新上次通知時間
                                    last_found_time = now
                            else:
                                    print(f"{current_time_str} - {label} 仍有票，但仍在 15 分鐘冷卻期內，不重複通知")
                except Exception as e:
                    print("KKTIX 查找過程中發生錯誤：", e)
            else:          
                # 查找"立即購買"按鈕的元素
                buy_button = driver.find_element(By.CSS_SELECTOR, ".v-btn__content")  # 替換為實際的CSS選擇器
                button_text = buy_button.text.strip()
                now = time.time()
                current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if "立即購買" in button_text:
                                if now - last_found_time >= cooldown:
                                    message = f"{label}\n{formatted_time}\n目前有清票 🎉\n購買網址: \n{url}"
                                    print(message)

                                # 發送到 LINE
                                send_line_message(
                                    to=LINE_GROUP_ID,
                                    messages=message
                                
                                )
                                # 等待 15 分鐘後重新檢查
                                print(f"{formatted_time} - 票已找到，等待 15 分鐘後重新檢查...")
                                # 更新上次通知時間
                                last_found_time = now
                                # 重新啟動檢查
                                driver.refresh()
                else:
                    print(f"{formatted_time}-{label}--沒找到票，繼續刷新...")

        except Exception as e:
            print("查找過程中發生錯誤：", e)
        time.sleep(check_interval)  

    driver.quit()

# 網址清單和對應的標籤
urls = [
    {"url": "https://ticketplus.com.tw/activity/42bc0a3283e8bc84372608fb016042bb", "label": "YOASOBI ASIA TOUR 2024-2025 Taipei"},
    {"url": "https://kktix.com/events/yuika2025/registrations/new", "label": "日本創作女聲『ユイカ』LIVE IN TAIPEI 2025"},
]

threads = []
for entry in urls:
    url = entry["url"]
    label = entry["label"]
    thread = threading.Thread(target=check_buy_button, args=(url, label, LINE_GROUP_ID))
    thread.start()
    threads.append(thread)

# 等待所有線程完成
for thread in threads:
    thread.join()
