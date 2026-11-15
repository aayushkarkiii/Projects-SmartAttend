import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "http://127.0.0.1:5050"

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        print("1. Capturing Login Page...")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "01_login.png"))

        print("2. Logging In...")
        page.fill('input[name="email"]', "admin@school.com")
        page.fill('input[name="password"]', "admin123")
        page.click('button[type="submit"]')
        page.wait_for_timeout(1000)

        print("3. Capturing Dashboard...")
        page.screenshot(path=os.path.join(OUTPUT_DIR, "02_dashboard.png"))

        print("4. Capturing Students Page...")
        page.goto(f"{BASE_URL}/students")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "03_students.png"))

        # 5. Live detector preview omitted for privacy


        print("6. Capturing Train Page...")
        page.goto(f"{BASE_URL}/train")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "05_train.png"))

        print("7. Capturing Attendance Logs Page...")
        page.goto(f"{BASE_URL}/attendance")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "06_attendance.png"))

        print("8. Capturing Developers / Team Page...")
        page.goto(f"{BASE_URL}/developers")
        page.wait_for_timeout(1000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "07_developers.png"))

        browser.close()
        print("ALL SCREENSHOTS CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    capture()
