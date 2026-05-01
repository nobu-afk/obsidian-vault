#!/usr/bin/env python3
"""
stock_watch.py - INPEX（1605）と川崎地質（4673）の株価を取得する
usage: python3 stock_watch.py [YYYY-MM-DD]
  日付指定なし → 直近5営業日を表示
  日付指定あり → その日の終値を表示
"""

import sys
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

TICKERS = {
    "INPEX": "1605.T",
    "川崎地質": "4673.T",
}

PURCHASE = {
    "INPEX": {"date": "2026-04-01", "price": 4623.75, "shares": 100},
}

def get_stock_data(period="5d"):
    results = {}
    for name, ticker in TICKERS.items():
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        if not hist.empty:
            results[name] = hist
    return results

def format_output(results, target_date=None):
    print("📊 株価データ取得")
    print()

    for name, hist in results.items():
        print(f"=== {name} ({TICKERS[name]}) ===")

        if target_date:
            # 特定日の終値を探す
            for idx, row in hist.iterrows():
                date_str = idx.strftime("%Y-%m-%d")
                if date_str == target_date:
                    close = row['Close']
                    print(f"  {target_date} 終値: {close:,.0f}円")

                    if name in PURCHASE:
                        p = PURCHASE[name]
                        pnl = (close - p['price']) * p['shares']
                        pnl_pct = (close - p['price']) / p['price'] * 100
                        print(f"  購入価格: {p['price']:,.2f}円 × {p['shares']}株")
                        print(f"  損益: {pnl:+,.0f}円 ({pnl_pct:+.1f}%)")
                    break
            else:
                print(f"  {target_date} のデータが見つかりません")
        else:
            # 直近5営業日を表示
            for idx, row in hist.iterrows():
                date_str = idx.strftime("%Y-%m-%d (%a)")
                close = row['Close']
                line = f"  {date_str}: {close:,.0f}円"

                if name in PURCHASE:
                    p = PURCHASE[name]
                    pnl = (close - p['price']) * p['shares']
                    pnl_pct = (close - p['price']) / p['price'] * 100
                    line += f"  [損益: {pnl:+,.0f}円 ({pnl_pct:+.1f}%)]"

                print(line)
        print()

    # マークダウンテーブル出力（コピペ用）
    print("--- 銘柄追跡ファイル用（コピペ） ---")
    latest_date = None
    for name, hist in results.items():
        if not hist.empty:
            latest = hist.iloc[-1]
            latest_date = hist.index[-1].strftime("%Y-%m-%d")
            prev = hist.iloc[-2] if len(hist) > 1 else None
            close = latest['Close']
            if prev is not None:
                diff = close - prev['Close']
                diff_pct = diff / prev['Close'] * 100
                print(f"{name}: {close:,.0f}円 (前日比 {diff:+,.0f}円, {diff_pct:+.1f}%)")
            else:
                print(f"{name}: {close:,.0f}円")

if __name__ == "__main__":
    target_date = None
    if len(sys.argv) > 1:
        target_date = sys.argv[1]

    results = get_stock_data()
    format_output(results, target_date)
