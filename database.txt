import sqlite3
from typing import List, Dict, Any

DB_NAME = "books.db"
TABLE_NAME = "llm_books"

def get_db_connection() -> sqlite3.Connection:
    #連接資料庫 (有 row_factory 可以用欄位名稱取值)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database() -> None:
    #建立資料表（如果還沒建)
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    title TEXT UNIQUE NOT NULL,
                    author TEXT,
                    price INTEGER,
                    link TEXT
                )
            """)
            conn.commit()
            print("資料庫初始化完成！")
    except sqlite3.Error as e:
        print("建立資料表時出錯：", e)


def bulk_insert_books(books: List[Dict[str, Any]]) -> int:
    #批量插入書籍資料，用 INSERT OR IGNORE 避免重複
    if not books:
        return 0

    count = 0
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            for b in books:
                cur.execute(f"""
                    INSERT OR IGNORE INTO {TABLE_NAME} (title, author, price, link)
                    VALUES (?, ?, ?, ?)
                """, (b['title'], b['author'], b['price'], b['link']))
                if cur.rowcount > 0:
                    count += 1
            conn.commit()
    except sqlite3.Error as e:
        print("新增資料時出錯：", e)
        return 0

    return count


def query_books(field: str, keyword: str) -> List[Dict[str, Any]]:
    #依欄位和關鍵字查詢書籍（LIKE 模糊比對)
    if field not in ["title", "author"]:
        print("欄位名稱不對喔，只能查 title 或 author。")
        return []

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT title, author, price, link
                FROM {TABLE_NAME}
                WHERE {field} LIKE ?
                ORDER BY price DESC
            """, (f"%{keyword}%",))
            data = [dict(row) for row in cur.fetchall()]
            return data
    except sqlite3.Error as e:
        print("查詢時發生錯誤：", e)
        return []
