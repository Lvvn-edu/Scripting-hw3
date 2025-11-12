import re
import time
from typing import List, Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

HOME_URL = "https://www.books.com.tw/"
SEARCH_KEYWORD = "LLM"

#如果Chrome無法啟動，請確認這裡的路徑
CHROME_BINARY_PATH: Optional[str] = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def clean_price(price_text: str) -> int:
    #從價格文字中取出數字
    match = re.search(r'[\d,]\s*(\d+)\s*元', price_text)
    if match:
        return int(match.group(1))
    nums = re.findall(r'\d+', price_text)
    return int(nums[-1]) if nums else 0


def parse_book_data(html_content: str) -> List[Dict[str, Any]]:
    #用BeautifulSoup解析單頁HTML抓書名、作者、價格、連結
    soup = BeautifulSoup(html_content, "html.parser")
    books = []

    box = soup.find("div", class_="table-searchbox")
    items = box.find_all("div", class_="table-td") if box else []

    for i in items:
        title, author, price, link = "N/A", "N/A", 0, "N/A"

        # 書名 + 連結
        t_tag = i.find("h4")
        if t_tag and t_tag.a:
            title = t_tag.a.text.strip()
            link = t_tag.a.get("href", "N/A")
            if not link.startswith("http"):
                link = f"https://www.books.com.tw{link}"

        # 作者
        a_tag = i.find("p", class_="author")
        if a_tag:
            author_list = [a.text.strip() for a in a_tag.find_all("a")]
            author = ", ".join(author_list) if author_list else "N/A"

        # 價格
        p_tag = i.find("p", class_="price_box")
        if p_tag:
            price = clean_price(p_tag.get_text(" ", strip=True))

        books.append({
            "title": title,
            "author": author,
            "price": price,
            "link": link
        })
    return books


def scrape_books() -> List[Dict[str, Any]]:
    """爬取博客來「LLM」書籍"""
    all_books = []
    page_num = 1
    total_pages = 0

    print("開始從網路爬取最新書籍資料...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    if CHROME_BINARY_PATH:
        chrome_options.binary_location = CHROME_BINARY_PATH

    driver = None
    try:
        driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=chrome_options)
        driver.get(HOME_URL)

        # 搜尋關鍵字
        print(f"正在搜尋關鍵字：{SEARCH_KEYWORD}")
        search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "key")))
        search_input.send_keys(SEARCH_KEYWORD)
        driver.find_element(By.CLASS_NAME, "searchgo").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "search_ap")))
        time.sleep(1)

        # 點擊「圖書」分類
        try:
            print("切換到『圖書』分類中...")
            link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="cat/BKA"]')))
            link.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table-searchbox")))
            time.sleep(1)
        except:
            print("沒找到圖書分類，可能已在該頁。")

        # 嘗試取得總頁數
        try:
            total_elem = driver.find_element(By.CSS_SELECTOR, 'div.page_box.search_page .cnt > span:nth-of-type(2)')
            total_pages = int(re.search(r'\d+', total_elem.text).group(0))
            print(f"偵測到總共有 {total_pages} 頁。")
        except:
            total_pages = 1

        # 開始爬每頁
        while True:
            print(f"正在爬第 {page_num} / {total_pages if total_pages else '?'} 頁...")
            html = driver.page_source
            all_books.extend(parse_book_data(html))

            try:
                next_page = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.page_btn.next')))
                next_page.click()
                page_num += 1
                time.sleep(1.5)
            except TimeoutException:
                print("爬到最後一頁啦～")
                break
    except Exception as e:
        print("爬蟲出問題了：", e)
    finally:
        if driver:
            driver.quit()

    print("爬取完成！")
    return all_books
