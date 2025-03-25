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

    # 進入 autogen 資料夾
    page.goto(f"{GITHUB_REPO_URL}/tree/main/autogen")
    page.wait_for_timeout(3000)

    # 點擊 "Add file" 按鈕
    try:
        # 等待 "Add file" 按鈕出現並點擊
        page.wait_for_selector("button:has-text('Add file')", timeout=10000)
        page.locator("button:has-text('Add file')").click()

        # 點擊 "Create new file" 按鈕
        page.wait_for_selector("a[role='menuitem']:has-text('Create new file')", timeout=10000)
        page.locator("a[role='menuitem']:has-text('Create new file')").click()

        # 填寫檔案名稱
        file_name = "Autogen_Learning.md"
        page.fill("input[aria-label='File name']", file_name)

        # 等待並確保可以填寫內容區域
        page.wait_for_selector("div.cm-content[contenteditable='true']", timeout=10000)

        # 使用 keyboard.type() 輸入內容到編輯區域
        page.locator("div.cm-content[contenteditable='true']").click()
        page.keyboard.type(
            "# Autogen Learning\n\nThis is a Markdown file discussing the **autogen learning** process.",
            delay=50
        )

        # 等待並點擊第一個提交按鈕 "Commit changes..."
        page.wait_for_selector("button:has-text('Commit changes...')", timeout=10000)
        page.locator("button:has-text('Commit changes...')").click()

        # 點擊第二個提交按鈕 "Commit changes"
        page.wait_for_selector("button[aria-disabled='false']:has-text('Commit changes')", timeout=10000)
        page.locator("button[aria-disabled='false']:has-text('Commit changes')").click()


        print("Markdown 檔案已提交！")
        page.screenshot(path="debug_2_after_commit.png")
    except Exception as e:
        print("出現錯誤：", e)

    # 保持瀏覽器開啟，方便 Debug
    input("瀏覽器保持開啟，按 Enter 關閉...")

    # 關閉瀏覽器
    browser.close()
    print("瀏覽器已關閉")
