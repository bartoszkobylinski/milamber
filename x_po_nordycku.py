import subprocess
import time
import json
from datetime import datetime, date

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ——————————————————————————————————————————————
# KONFIGURACJA
USERNAME    = "Po_nordycku"
START_DATE  = date(2025, 5, 1)
END_DATE    = date(2025, 5, 31)
OUTPUT_FILE = f"{USERNAME}_tweets_may2025_selenium_visible.json"

CHROME_BINARY = (
    "/Applications/Google Chrome for Testing.app/"
    "Contents/MacOS/Google Chrome for Testing"
)
# ——————————————————————————————————————————————

# 1) Wykryj wersję Chrome i uruchom driver
print("Detecting Chrome version...")
version_raw = subprocess.check_output(
    [CHROME_BINARY, "--version"], stderr=subprocess.DEVNULL
).decode().strip()
version = version_raw.split()[-1]
print(f"Detected Chrome version: {version}")

print("Setting up Selenium options (visible)...")
options = webdriver.ChromeOptions()
options.binary_location = CHROME_BINARY
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

service = Service(ChromeDriverManager(driver_version=version).install())
driver = webdriver.Chrome(service=service, options=options)
print("WebDriver started successfully")

try:
    # 2) Najpierw ręczne logowanie + cookies
    print("Otwieram stronę logowania X…")
    driver.get("https://x.com/login")
    time.sleep(3)
    print("""
    ▶️ ZALOGUJ SIĘ TERAZ RĘCZNIE W PRZEGLĄDARCE:
      • wpisz login i hasło,
      • zaakceptuj baner ciasteczek,
    a potem wróć do terminala i naciśnij Enter, żeby kontynuować…""")
    input()  # czekamy, aż użytkownik kliknie Enter

    # 3) Teraz scrapowanie na Twoim profilu
    url = f"https://x.com/{USERNAME}"
    print(f"Ładuję profil: {url}")
    driver.get(url)
    time.sleep(5)

    collected = set()
    tweets = []
    keep_scrolling = True
    iteration = 0

    while keep_scrolling:
        iteration += 1
        print(f"Iteration {iteration}: locating tweets on page")
        articles = driver.find_elements(By.TAG_NAME, "article")
        print(f"Found {len(articles)} articles")

        for art in articles:
            try:
                tm = art.find_element(By.TAG_NAME, "time")
                dt = datetime.fromisoformat(
                    tm.get_attribute("datetime").replace("Z", "+00:00")
                )
                td = dt.date()
            except Exception:
                continue

            if td < START_DATE:
                print(f"Tweet dated {td} is older than {START_DATE}. Stopping.")
                keep_scrolling = False
                continue

            if START_DATE <= td <= END_DATE:
                try:
                    link = art.find_element(
                        By.XPATH, ".//a[contains(@href, '/status/')]"
                    )
                    url = link.get_attribute("href")
                    tid = url.rsplit("/", 1)[-1]
                except:
                    continue

                try:
                    content = art.find_element(
                        By.CSS_SELECTOR, "div[data-testid='tweetText']"
                    ).text
                except NoSuchElementException:
                    content = ""

                if tid not in collected:
                    tweets.append({
                        "id": tid,
                        "date": dt.isoformat(),
                        "content": content,
                        "url": url
                    })
                    collected.add(tid)
                    print(f"Collected tweet {tid} dated {td}")

        if keep_scrolling:
            print("Scrolling for more tweets…")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

    print(f"Scraping complete. Total tweets collected: {len(tweets)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    print(f"Results saved to {OUTPUT_FILE}")

finally:
    print("Quitting WebDriver…")
    driver.quit()
    print("WebDriver session ended")
