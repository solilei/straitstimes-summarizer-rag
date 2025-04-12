from bs4 import BeautifulSoup
import requests
from requests import RequestException


class Scraper:
    def __init__(self):
        self.url = None
        self.max_articles = 8
        self.article_urls = None
        self.all_texts = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) "
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}

    def get_initial_url(self):
        available_topics = ["Singapore", "Asia", "World", "Life", "Tech", "Sport", "Business"]

        print(f"Welcome to The Straits Times summarizer!\n\n"
              f"These are the available topics: \n{available_topics}\n")
        while True:
            user_topic = input("Please choose your topic: ").strip()
            if user_topic.title() not in available_topics:
                print("Error, please choose from the provided list.")
            else:
                user_topic = user_topic.lower()
                break
        self.url = "https://www.straitstimes.com/" + user_topic

    def get_url_list(self):
        self.get_initial_url()
        try:
            page = requests.get(self.url, headers=self.headers, timeout=10)
            page.raise_for_status()
            main_page = BeautifulSoup(page.content, "html.parser")

        except Exception as e:
            raise RequestException(f"Error: {str(e)}")

        containers = main_page.find_all("a", {"class": "card-link card-detail"}, href=True)
        article_urls = []

        for container in containers[:self.max_articles]:
            url = container.get("href")
            print(f"URL scraped: {url}")
            full_url = "https://www.straitstimes.com" + url
            article_urls.append(full_url)

        self.article_urls = article_urls

        return article_urls

    def get_articles_list(self):
        url_list = self.get_url_list()
        all_texts = []

        for url in url_list:
            page = requests.get(url)

            article_page = BeautifulSoup(page.content, "html.parser")
            texts = article_page.find_all("p", {"class": "paragraph-base"})
            full_text = []

            for text in texts:
                cleaned_line = text.get_text(strip=True).replace(u'\xa0', u' ')
                full_text.append(cleaned_line)

            full_text = " ".join(full_text)

            if full_text:
                all_texts.append(full_text)

        self.all_texts = all_texts

        return all_texts
