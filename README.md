# Amazon Wishlist Tracker

Amazonの公開欲しい物リストを定期的に監視し、価格変動があればLINEに通知するPythonスクリプトです。

## 機能
- Amazon公開欲しい物リストをスクレイピング
- SQLiteで価格履歴を保存
- 前回価格と今回価格が異なる場合、LINE Notifyで通知
- VPSやPCでcron実行可能

## 必要環境
- Python 3.8+
- Amazon欲しい物リスト（公開設定）
- LINE Notify アクセストークン

## インストール
```bash
git clone https://github.com/yourname/wishlist-tracker.git
cd wishlist-tracker
pip install -r requirements.txt
cp .env.example .env
```

## .env 設定
```bash
WISHLIST_URL=https://www.amazon.jp/hz/wishlist/ls/XXXXXXXXXXXXX
LINE_TOKEN=your_line_notify_token
```

## 実行
```bash
python main.py
```

## 定期実行（cron）

1時間ごとに実行する例：
```bash
0 * * * * /usr/bin/python3 /path/to/wishlist-tracker/main.py
```

---

# Amazon Wishlist Tracker (English)

A Python script that monitors a public Amazon wishlist and sends a LINE notification when prices change.

## Features
- Scrapes public Amazon wishlist
- Stores price history in SQLite
- Sends LINE Notify message if price changes
- Works with cron jobs on VPS or local PC

## Requirements
- Python 3.8+
- Public Amazon Wishlist URL
- LINE Notify Access Token

## Installation
```bash
git clone https://github.com/yourname/wishlist-tracker.git
cd wishlist-tracker
pip install -r requirements.txt
cp .env.example .env
```

## .env Configuration
```bash
WISHLIST_URL=https://www.amazon.jp/hz/wishlist/ls/XXXXXXXXXXXXX
LINE_TOKEN=your_line_notify_token
```

## Run
```bash
python main.py
```

## Schedule with cron
Run every hour:
```bash
0 * * * * /usr/bin/python3 /path/to/wishlist-tracker/main.py
```

---
