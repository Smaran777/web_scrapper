# scraper.py
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import pandas as pd

def scrape_website(base_url, max_pages=30):
    visited = set()
    data = []
    queue = [base_url]

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited or not url.startswith(base_url):
            continue

        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'N/A'
            text = soup.get_text(strip=True)[:1000]  # limit text length
            meta = soup.find_all('meta')
            meta_data = '; '.join([m.get('content') or '' for m in meta if m.get('content')])

            data.append({'URL': url, 'Title': title, 'Text': text, 'Meta': meta_data})
            visited.add(url)

            for link in soup.find_all('a', href=True):
                full_url = urljoin(base_url, link['href'])
                if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in visited:
                    queue.append(full_url)

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    return pd.DataFrame(data)
