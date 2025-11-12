# Scripting-hw3
專案結構
app.py: 程式主入口點，提供 CLI 選單介面。
scraper.py: 負責網頁爬取邏輯，使用 Selenium 處理分頁和資料擷取。
database.py: 負責 SQLite 資料庫的初始化、批量儲存和查詢功能。
程式啟動後會顯示主選單：
1更新書籍資料庫：啟動 Selenium 爬蟲，抓取博客來所有分頁的 LLM 書籍資料，並使用 INSERT OR IGNORE 語法將新書記錄存入 books.db。
2查詢書籍：提供子選單，可選擇依「書名」或「作者」進行模糊關鍵字查詢。
3離開系統：結束程式運行。
若要查詢書籍
a依書名查詢
b依作者查詢
c返回主選單
