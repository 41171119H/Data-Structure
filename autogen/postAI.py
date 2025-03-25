from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

# 讀取 .env 檔案
load_dotenv()
GITHUB_EMAIL = os.getenv("GITHUB_EMAIL")
GITHUB_PASSWORD = os.getenv("GITHUB_PASSWORD")
GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 顯示瀏覽器
    page = browser.new_page()

    print("啟動瀏覽器，開始登入 GitHub...")

    # 進入 GitHub 登入頁面
    page.goto("https://github.com/login")
    page.wait_for_timeout(3000)

    # 使用 .env 讀取帳號密碼 : 確認html, 透過playwright 提取 DOM
    page.fill("#login_field", GITHUB_EMAIL)
    page.fill("#password", GITHUB_PASSWORD)

    # 按下登入按鈕
    page.press("#password", "Enter")

    # 等待 2FA 驗證
    print("現在需要手動完成 2FA 驗證:")
    input("請手動完成 2FA 驗證，然後按 Enter 繼續...")

    # 等待登入完成
    page.wait_for_timeout(5000)
    print("登入成功！")
    page.screenshot(path="debug_1_after_login.png")

    # 進入指定的 GitHub 倉庫頁面
    page.goto(GITHUB_REPO_URL)
    page.wait_for_timeout(3000)
    print("進入 GitHub Repo")

    # 檢查資料夾是否存在
    folder_path = "Data-Structure/autogen"
    # page.goto(f"{GITHUB_REPO_URL}/tree/main/Data-Structure")
    page.goto(f"{GITHUB_REPO_URL}/tree/main/autogen")
    page.wait_for_timeout(3000)

    if "404 Not Found" in page.content():
        print(f"資料夾 {folder_path} 不存在，正在建立...")

        # 點擊 "Add file" 並選擇 "Create new file"
        page.locator("button:has-text('Add file')").click()
        page.wait_for_timeout(2000)
        page.locator("button:has-text('Create new file')").click()

        # 填寫資料夾路徑和 Markdown 檔案名稱及內容
        file_name = f"Data-Structure/autogen/Autogen_Learning.md"
        page.fill("input[name='path']", file_name)
        page.fill("div[aria-label='Text editor'] textarea", 
                  "# Autogen Learning\n\nThis is a Markdown file discussing the **autogen learning** process.")

        # 提交檔案，先填寫 commit 訊息
        page.fill("input[name='commit-message']", "Add autogen learning Markdown")
        page.click("button:has-text('Commit new file')")

        print("Markdown 檔案已提交！")
        page.screenshot(path="debug_2_after_commit.png")
    else:
        print(f"資料夾 {folder_path} 已存在，直接創建檔案...")

        # 點擊 "Add file" 並選擇 "Create new file"
        page.locator("button:has-text('Add file')").click()
        page.wait_for_timeout(2000)
        page.locator("button:has-text('Create new file')").click()

        # 填寫資料夾路徑和 Markdown 檔案名稱及內容
        file_name = f"Data-Structure/autogen/Autogen_Learning.md"
        page.fill("input[name='path']", file_name)
        page.fill("div[aria-label='Text editor'] textarea", 
                  "# Autogen Learning\n\nThis is a Markdown file discussing the **autogen learning** process.")

        # 提交檔案，先填寫 commit 訊息
        page.fill("input[name='commit-message']", "Add autogen learning Markdown")
        page.click("button:has-text('Commit new file')")

        print("Markdown 檔案已提交！")
        page.screenshot(path="debug_2_after_commit.png")

    # 保持瀏覽器開啟，方便 Debug
    input("瀏覽器保持開啟，按 Enter 關閉...")

    # 關閉瀏覽器
    browser.close()
    print("瀏覽器已關閉")
