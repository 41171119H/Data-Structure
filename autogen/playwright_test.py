from playwright.sync_api import sync_playwright

def test_playwright_connection(url="https://www.google.com"):
    try:
        with sync_playwright() as p:
            # 啟用無頭模式並設置超時時間
            browser = p.chromium.launch(headless=True, timeout=60000)
            page = browser.new_page()
            response = page.goto(url)
            print(f"連線成功！狀態碼：{response.status}")
            browser.close()
            return True
    except Exception as e:
        print(f"連線失敗：{e}")
        return False

if __name__ == "__main__":
    if test_playwright_connection():
        print("Playwright 功能正常")
    else:
        print("Playwright 功能異常")
