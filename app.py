import sys
from typing import List, Dict, Any

try:
    from scraper import scrape_books
    from database import bulk_insert_books, query_books, setup_database
except ImportError:
    print("找不到必要模組 (scraper.py或database.py)，請確認檔案有放在同一資料夾！")
    sys.exit(1)


def display_main_menu() -> None:
    print("\n" + "-" * 35)
    print("----- 博客來 LLM 書籍管理系統 -----")
    print("1. 更新書籍資料庫")
    print("2. 查詢書籍")
    print("3. 離開系統")
    print("-" * 35)


def display_query_menu() -> None:
    print("\n--- 查詢書籍 ---")
    print("a. 依書名查詢")
    print("b. 依作者查詢")
    print("c. 返回主選單")
    print("-" * 15)


def update_database_action() -> None:
    #爬蟲 + 更新資料庫
    try:
        books = scrape_books()
    except Exception as e:
        print("爬蟲失敗:", e)
        return

    total = len(books)
    if total == 0:
        print("沒有抓到任何書籍，資料庫沒有更新。")
        return

    try:
        setup_database()
        new_count = bulk_insert_books(books)
        print(f"資料庫更新完成！共爬取 {total} 筆資料，新增 {new_count} 筆新書。")
    except Exception as e:
        print("更新資料庫時出錯：", e)


def search_and_display(field: str, keyword: str) -> None:
    #查詢資料並輸出
    try:
        data = query_books(field, keyword)
    except Exception as e:
        print("查詢時出錯：", e)
        return

    if not data:
        print("查無資料。")
        return

    print("\n" + "=" * 20)
    for book in data:
        print(f"書名：{book['title']}")
        print(f"作者：{book['author']}")
        print(f"價格：{book['price']}")
        print("---")
    print("=" * 20)


def query_books_action() -> None:
    #查詢選單
    while True:
        display_query_menu()
        ch = input("請選擇查詢方式 (a-c): ").strip().lower()

        if ch == "c":
            break
        elif ch in ["a", "b"]:
            keyword = input("請輸入關鍵字: ").strip()
            if not keyword:
                print("關鍵字不能是空的啦。")
                continue
            field = "title" if ch == "a" else "author"
            search_and_display(field, keyword)
        else:
            print("無效選項，請重新輸入。")


def main():
    #主程式入口
    setup_database()

    while True:
        display_main_menu()
        opt = input("請選擇操作選項 (1-3): ").strip()

        if opt == "1":
            update_database_action()
        elif opt == "2":
            query_books_action()
        elif opt == "3":
            print("系統結束")
            break
        else:
            print("選項不對，再試一次。")


if __name__ == "__main__":
    main()

