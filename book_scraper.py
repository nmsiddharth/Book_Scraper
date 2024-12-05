import json
import os
import requests
from bs4 import BeautifulSoup
import logging

class BookScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.all_books = []  # List to store all book details

    def fetch_page_content(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Check if the request was successful (status code 200)
            return response.text  # Return the page content as a string
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None  # Return None if there was an error

    def parse_books(self, page_content):
        # Parse book details from a single page's HTML content.
        soup = BeautifulSoup(page_content, "lxml")  # Contains HTML code
        books = []  # List to store parsed book details

        # Loop through each book on the page (identified by the 'article' tag with 'product_pod' class)
        for book in soup.find_all("article", class_='product_pod'):
            # Extract book details:
            title = book.h3.a["title"]
            price = book.find("p", class_="price_color").text.strip()
            stock = book.find("p", class_="instock availability").text.strip()
            rating = book.find("p", class_="star-rating")["class"][1]  # class attribute contains 2 elements, one is "star_rating" and another is "one/two/three/four/five"
            image_url = self.base_url + book.find("img")["src"].replace("../", "")

            # Append the book details as a dictionary of books
            books.append({
                "Title": title,
                "Price": price,
                "Stock": stock,
                "Rating": rating,
                "Image URL": image_url
            })

        return books

    def scrape_books(self):
        # scrape all books from multiple pages.
        page_number = 1
        while True:
            logging.info(f"Scraping page {page_number}...")  # Logs which page is being scraped
            url = f"{self.base_url}/catalogue/page-{page_number}.html"  # construct url of the page
            page_content = self.fetch_page_content(url)
            if page_content:
                books = self.parse_books(page_content)
                if books:  # If books were found
                    self.all_books.extend(books)  # Add books list to all books list
                    page_number += 1
                else:
                    logging.info("No more books found. Scraping complete!")
                    break
            else:
                logging.error("Failed to fetch page. Ending scrape.")
                break

    def save_to_json(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(self.all_books, json_file, ensure_ascii=False, indent=4)     # ensure_ascii = False, ensures that characters like é, ü, or Chinese/Japanese characters are saved in their original form, making the output JSON file both more accurate and readable.
        logging.info(f"Data saved to {filename}")

# Main Workflow
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Set the logging level to Info
    BASE_URL = "http://books.toscrape.com"  # Base URL of the website to scrape
    scrapper = BookScraper(BASE_URL)  # Instantiate the scraper object
    scrapper.scrape_books()
    scrapper.save_to_json("books_data.json")
