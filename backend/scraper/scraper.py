import logging
import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from .parser import parse_listing_page, parse_detail_page
from books.models import Book

logger = logging.getLogger(__name__)

class BookScraper:
    def __init__(self, base_url="https://books.toscrape.com", max_pages=3):
        self.base_url = base_url.rstrip('/')
        self.max_pages = max_pages
        self.driver = None

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def scrape_listing_page(self, page_url) -> list[dict]:
        self.driver.get(page_url)
        time.sleep(1) # polite jitter
        return parse_listing_page(self.driver.page_source)

    def scrape_book_detail(self, book_url) -> dict:
        self.driver.get(book_url)
        time.sleep(0.5)
        return parse_detail_page(self.driver.page_source)

    def run(self):
        logger.info(f"Starting scraper for {self.base_url}")
        self.setup_driver()
        scraped_books = []
        
        try:
            for page_num in range(1, self.max_pages + 1):
                page_url = f"{self.base_url}/catalogue/page-{page_num}.html"
                if page_num == 1:
                    page_url = f"{self.base_url}/index.html"
                
                logger.info(f"Scraping list page: {page_url}")
                try:
                    books_data = self.scrape_listing_page(page_url)
                except Exception as e:
                    logger.error(f"Error scraping listing page {page_url}: {e}")
                    continue
                
                for b in books_data:
                    if 'catalogue' not in b['url_suffix'] and page_num == 1:
                        full_book_url = urljoin(self.base_url, f"catalogue/{b['url_suffix']}")
                    else:
                        base_for_join = f"{self.base_url}/catalogue/" if 'catalogue' not in self.driver.current_url else self.driver.current_url
                        full_book_url = urljoin(base_for_join, b['url_suffix'])
                        
                    cover_full_url = urljoin(self.base_url, b['cover_image_slug'])
                    
                    if Book.objects.filter(book_url=full_book_url).exists():
                        continue
                        
                    logger.info(f"Scraping detail: {full_book_url}")
                    try:
                        detail_data = self.scrape_book_detail(full_book_url)
                    except Exception as e:
                        logger.error(f"Error scraping detail {full_book_url}: {e}")
                        continue
                        
                    book = Book.objects.create(
                        title=b['title'],
                        book_url=full_book_url,
                        price=b['price'],
                        rating=b['rating'],
                        cover_image_url=cover_full_url,
                        description=detail_data.get('description', ''),
                        genre=detail_data.get('genre', ''),
                        reviews_count=detail_data.get('reviews_count', 0),
                        author=detail_data.get('author', 'Unknown')
                    )
                    scraped_books.append(book.id)
                    
        finally:
            if self.driver:
                self.driver.quit()
                
        return scraped_books
