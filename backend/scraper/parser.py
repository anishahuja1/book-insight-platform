from bs4 import BeautifulSoup
import re

def parse_listing_page(html_content: str) -> list[dict]:
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []
    
    articles = soup.find_all('article', class_='product_pod')
    for article in articles:
        title_a = article.find('h3').find('a')
        title = title_a.get('title', title_a.text)
        
        url = title_a.get('href')
        
        price_p = article.find('p', class_='price_color')
        price = price_p.text if price_p else ""
        
        star_p = article.find('p', class_='star-rating')
        rating_classes = star_p.get('class', []) if star_p else []
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating = None
        for r_class in rating_classes:
            if r_class in rating_map:
                rating = float(rating_map[r_class])
                
        img = article.find('img')
        cover = img.get('src', '') if img else ''
        
        books.append({
            'title': title,
            'url_suffix': url,
            'price': price,
            'rating': rating,
            'cover_image_slug': cover
        })
    return books

def parse_detail_page(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    desc_tag = soup.find('div', id='product_description')
    description = ""
    if desc_tag and desc_tag.find_next_sibling('p'):
        description = desc_tag.find_next_sibling('p').text
        
    breadcrumb = soup.find('ul', class_='breadcrumb')
    genre = ""
    if breadcrumb:
        links = breadcrumb.find_all('a')
        if len(links) >= 3:
            genre = links[2].text.strip()
            
    reviews_count = 0
    table = soup.find('table', class_='table table-striped')
    if table:
        th = table.find('th', string='Number of reviews')
        if th and th.find_next_sibling('td'):
            try:
                reviews_count = int(th.find_next_sibling('td').text)
            except:
                pass
                
    return {
        'description': description,
        'genre': genre,
        'reviews_count': reviews_count,
        'author': 'Unknown'
    }
