import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import urllib.request
import time
from datetime import datetime
import requests
import re
import pandas as pd

class Crawler:
    def __init__(self, start_url, max_urls=50, max_links=5, use_sitemap=True):
        self.start_url = start_url
        self.max_urls = max_urls
        self.max_links = max_links
        self.use_sitemap = use_sitemap
        self.visited_urls = []
        self.crawled_urls = []
        self.queue = [start_url]
        self._rp = {}
        self.useragent = "*"
        self.df = pd.DataFrame(columns=['url','last_crawling'])

    def get_sitemap_urls_from_robots(self, robots_url):
        try:
            # Télécharger le contenu du fichier robots.txt
            response = requests.get(robots_url)
            response.raise_for_status()

            # Extraire les adresses de sitemap à l'aide d'une expression régulière
            sitemap_matches = re.findall(r'^\s*Sitemap:\s*(.*?)(?:\r)?$', response.text, re.M | re.I)
            while sitemap_matches:
                sitemap_entry = sitemap_matches.pop(0)
                response_entry = urllib.request.urlopen(sitemap_entry)
                xml = BeautifulSoup(response_entry,'lxml-xml',from_encoding=response_entry.info().get_param('charset'))
                if xml.find_all('sitemapindex'):
                    sitemaps = xml.find_all("sitemap")
                    for sitemap in sitemaps:
                        loc_map = sitemap.findNext("loc").text
                        if not loc_map in sitemap_matches:
                            sitemap_matches.append(loc_map)
                elif xml.find_all('urlset'):
                    urls = xml.find_all("url")
                    for url in urls:
                        if xml.find("loc"):
                            loc_url = url.findNext("loc").text
                            if not loc_url in self.queue:
                                self.queue.append(loc_url)
                else:
                    print("Error while reading sitemap")

        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération du fichier robots.txt : {e}")

    def is_allowed(self, url):
        url_struct = urlparse(url)
        base = url_struct.netloc
        # look up in the cache or update it
        if base not in self._rp:
            self._rp[base] = RobotFileParser()
            self._rp[base].set_url(url_struct.scheme + "://" + base + "/robots.txt")
            self._rp[base].read()
            if self._rp[base].can_fetch(self.useragent, url) and self.use_sitemap:
                self.get_sitemap_urls_from_robots(url_struct.scheme + "://" + base + "/robots.txt")
                print("Récupération du sitemap depuis : " + url_struct.scheme + "://" + base + "/robots.txt")
        return self._rp[base].can_fetch(self.useragent, url)

    def crawl_url(self, url):
        try:
            if not self.is_allowed(url):
                print(f"Not allowed to crawl: {url}")
                return None

            print(f"Crawling: {url}")
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return None

    def extract_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True) if a.get('href').startswith('http')]
        return links

    def save_to_file(self):
        with open('crawled_webpages.txt', 'w') as file:
            for url in self.crawled_urls:
                file.write(url + '\n')

    def run_crawler(self):
        while self.queue and len(self.crawled_urls) < self.max_urls:
            current_url = self.queue.pop(0)

            if current_url not in self.visited_urls:
                print(f"Visiting: {current_url}")
                self.visited_urls.append(current_url)
                start_time = time.time()
                html = self.crawl_url(current_url)

                if html:
                    self.crawled_urls.append(current_url)
                    timestamp = time.time()
                    datetime_obj = datetime.fromtimestamp(timestamp)
                    formatted_date = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
                    row = pd.DataFrame({
                        'url': [current_url],
                        'last_crawling': [formatted_date]
                    })
                    self.df = pd.concat([self.df, row], ignore_index=True)
                    links = self.extract_links(html)
                    if self.max_links == 'all':
                        self.queue.extend(links)
                    else:
                        self.queue.extend(links[:self.max_links])

                end_time = time.time()
                elapsed_time = end_time - start_time

                time.sleep(max(0.5,3 - elapsed_time))  # Respecter la politesse en attendant 3 secondes entre chaque appel moins la part variable

        self.save_to_file()

        print(f"Crawling finished. {len(self.crawled_urls)} URLs found and saved to crawled_webpages.txt")
        print(self.df.head()) #Affichage des 5 premières ligne de la base de données

if __name__ == '__main__':
    # Example usage 
    crawler = Crawler("https://ensai.fr/", max_urls=10, max_links='all')
    crawler.run_crawler()
