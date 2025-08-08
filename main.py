import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage

load_dotenv()

WISHLIST_URL = os.getenv("AMAZON_WISHLIST_URL")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wishlist.db")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9"
}

def create_table():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                id TEXT PRIMARY KEY,
                name TEXT,
                price INTEGER
            )
        """)
        conn.commit()

def fetch_wishlist():
    res = requests.get(WISHLIST_URL, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    items = []

    # ここはAmazonの欲しいものリストの構造によって調整が必要です
    for item_div in soup.select("div.g-item-sortable"):
        # 商品ID取得（ASINなど）
        link = item_div.select_one("a.a-link-normal")
        if not link:
            continue
        href = link.get("href", "")
        asin = None
        if "dp/" in href:
            asin = href.split("dp/")[1].split("/")[0]
        if not asin:
            continue

        # 商品名
        name_tag = item_div.select_one("a.a-link-normal")
        name = name_tag.text.strip() if name_tag else "名前不明"

        # 価格
        price_tag = item_div.select_one("span.a-price > span.a-offscreen")
        if price_tag:
            price_str = price_tag.text.strip().replace("￥", "").replace(",", "")
            try:
                price = int(price_str)
            except:
                price = None
        else:
            price = None

        items.append({"id": asin, "name": name, "price": price})

    return items

def check_and_notify():
    create_table()
    items = fetch_wishlist()

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        messages = []
        for item in items:
            c.execute("SELECT price FROM wishlist WHERE id=?", (item["id"],))
            row = c.fetchone()
            old_price = row[0] if row else None
            new_price = item["price"]

            if new_price is None:
                # 価格情報がない場合はスキップ
                continue

            if old_price is None:
                # 初回登録
                c.execute("INSERT OR REPLACE INTO wishlist (id, name, price) VALUES (?, ?, ?)",
                          (item["id"], item["name"], new_price))
            elif old_price != new_price:
                # 価格変動検知
                msg = f"【価格変動】\n{item['name']}\n前回: ￥{old_price}\n今回: ￥{new_price}"
                messages.append(msg)
                c.execute("UPDATE wishlist SET price=? WHERE id=?", (new_price, item["id"]))

        conn.commit()

    if messages:
        text = "\n\n".join(messages)
        try:
            line_bot_api.broadcast(TextSendMessage(text=text))
            print("通知送信完了")
        except Exception as e:
            print("通知送信エラー:", e)
    else:
        print("価格変動なし")

if __name__ == "__main__":
    check_and_notify()
