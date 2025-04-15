# app.py
import streamlit as st
from scraper import scrape_website
from report_generator import save_as_pdf, save_as_txt

st.title("Universal Web Scraper")
url = st.text_input("Enter a website URL:", "https://example.com")
depth = st.slider("Crawl Depth", 1, 3, 2)

if st.button("Start Scraping"):
    with st.spinner("Scraping in progress..."):
        scraped_data = scrape_website(url, depth)
        save_as_txt(scraped_data)
        save_as_pdf(scraped_data)
    st.success("Scraping Complete!")
    st.download_button("Download Report (TXT)", data=open("report.txt", "rb"), file_name="report.txt")
    st.download_button("Download Report (PDF)", data=open("report.pdf", "rb"), file_name="report.pdf")


# scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited_links = set()

def scrape_website(base_url, depth=2):
    content = []

    def crawl(url, current_depth):
        if current_depth > depth or url in visited_links:
            return
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return
            visited_links.add(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            content.append(f"\nURL: {url}\n{text}\n")

            for link in soup.find_all('a', href=True):
                absolute_link = urljoin(url, link['href'])
                if urlparse(absolute_link).netloc == urlparse(base_url).netloc:
                    crawl(absolute_link, current_depth + 1)

        except Exception as e:
            print(f"Failed to crawl {url}: {e}")

    crawl(base_url, 0)
    return content


# report_generator.py
from fpdf import FPDF

def save_as_pdf(data, filename='report.pdf'):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in data:
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)

def save_as_txt(data, filename='report.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for line in data:
            f.write(line + '\n')


# requirements.txt
streamlit
beautifulsoup4
requests
fpdf
