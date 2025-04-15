import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import streamlit as st
import time

# ---------- SCRAPER FUNCTION ----------
def get_all_links(base_url, max_pages=50):
    visited = set()
    to_visit = [base_url]
    product_links = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            response = requests.get(url, timeout=5)
            visited.add(url)
            soup = BeautifulSoup(response.text, "lxml")

            # Extract product info
            if "product" in url:
                product_links.append(url)

            # Find all internal links
            for link in soup.find_all("a", href=True):
                href = urljoin(base_url, link['href'])
                if urlparse(href).netloc == urlparse(base_url).netloc and href not in visited:
                    to_visit.append(href)
        except Exception as e:
            print("Error accessing:", url)
            continue

    return list(set(product_links))


def scrape_product_info(product_url):
    try:
        response = requests.get(product_url)
        soup = BeautifulSoup(response.text, "lxml")

        title = soup.find("h4", class_="title").text.strip() if soup.find("h4", class_="title") else ""
        price = soup.find("h4", class_="price").text.strip() if soup.find("h4", class_="price") else ""
        description = soup.find("p", class_="description").text.strip() if soup.find("p", class_="description") else ""
        reviews = soup.find("p", class_="pull-right").text.strip() if soup.find("p", class_="pull-right") else ""

        return {
            "URL": product_url,
            "Title": title,
            "Price": price,
            "Description": description,
            "Reviews": reviews
        }
    except Exception as e:
        return {
            "URL": product_url,
            "Title": "Error",
            "Price": "",
            "Description": "",
            "Reviews": ""
        }

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="E-commerce Web Scraper", layout="wide")
st.title("🛍️ E-commerce Web Scraper")
st.write("Scrapes products from a demo e-commerce site and exports to CSV")

base_url = "https://webscraper.io/test-sites/e-commerce/static"
if st.button("Start Scraping"):
    with st.spinner("Scraping subpages..."):
        links = get_all_links(base_url)
        st.success(f"Found {len(links)} product pages")

        results = []
        progress = st.progress(0)
        for i, link in enumerate(links):
            info = scrape_product_info(link)
            results.append(info)
            progress.progress((i + 1) / len(links))

        df = pd.DataFrame(results)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Report as CSV",
            csv,
            "ecommerce_report.csv",
            "text/csv"
        )

        st.success("✅ Done!")
