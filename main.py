import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

# .env を読み込み
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

# 環境変数取得
WISHLIST_URL = os.getenv("WISHLIST_URL")
LINE_TOKEN = os.getenv("LINE_TOKEN")

if not WISHLIST_URL or not LINE_TOKEN:
    raise ValueError(".env に WISHLIST_URL と LINE_TOKEN を設定してください")

# データベース設定
DB_PATH = os.path.join(BASE_DIR, "wishlist.db")

# LINE通知関数
def send_line_notify(message: str):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    payload = {"message": message}
    requests.post(url, headers=headers, data=payload)

# スクレイピング関数
def scrape_wishlist():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(WISHLIST_URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    items = []

    for item in soup.select(".g-item-sortable"):
        title_elem = item.select_one(".a-text-normal")
        price_elem = item.select_one(".a-price .a-offscreen")

        if title_elem and price_elem:
            title = title_elem.get_text(strip=True)
            price_text = price_elem.get_text(strip=True).replace("￥", "").replace(",", "")
            try:
                price = int(price_text)
            except ValueError:
                continue
            items.append((title, price))

    return items

# データベース初期化
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            last_updated TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# 価格比較と更新
def check_and_update_prices(items):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for title, price in items:
        c.execute("SELECT price FROM wishlist WHERE title = ?", (title,))
        row = c.fetchone()
        if row:
            old_price = row[0]
            if old_price != price:
                send_line_notify(
                    f"📢 Amazon欲しい物リスト価格変動\n"
                    f"{title}\n"
                    f"前回: ￥{old_price:,}\n"
                    f"今回: ￥{price:,}"
                )
                c.execute(
                    "UPDATE wishlist SET price = ?, last_updated = ? WHERE title = ?",
                    (price, datetime.now().isoformat(), title)
                )
        else:
            c.execute(
                "INSERT INTO wishlist (title, price, last_updated) VALUES (?, ?, ?)",
                (title, price, datetime.now().isoformat())
            )

    conn.commit()
    conn.close()

# メイン処理
if __name__ == "__main__":
    init_db()
    items = scrape_wishlist()
    check_and_update_prices(items)
