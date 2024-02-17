
"""

webscrape_bbc_wwc2023.py
Script that scrapes  BBC Women's World Cup 2023 site for article content

https://www.bbc.com/sport/football/womens-world-cup


python webscraper_bbc_wwc2023.py

"""

from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
from pathlib import Path

FRONT_PAGE_URL = "https://www.bbc.com/sport/football/womens-world-cup"
BASE_URL = "https://www.bbc.com"
SCORES_FIXTURES_URL = "https://www.bbc.com/sport/football/womens-world-cup/scores-fixtures"

class BBCWWCScraper:
    """
    Class that scrapes a BBC Women's World Cup site

    """
    def __init__(self):
        """
            Creates download directory if it doesn't exist
        """
        self.visited_urls = []
        self.destdir = "/tmp/wwc2023"
        Path(self.destdir).mkdir(parents=True, exist_ok=True)


    def scrape_front_page(self):
        """
          Using patterns obtained by inspection, scrape front page links.
          For each link, visit page and download content
        """
        html_content = requests.get(FRONT_PAGE_URL).text
        soup = BeautifulSoup(html_content, "html.parser")

        classes = ["ssrcss-zmz0hi-PromoLink exn3ah91", "ssrcss-vdnb7q-PromoLink exn3ah91"]
        tags = ["a"]
        scraper = soup.find_all(tags, attrs={'class': classes})
        scraper_data = [{i.get('href'):i.get_text()} for i in scraper if i.get('href').startswith('/sport')]
        scraper_paths = [i.get('href') for i in scraper if i.get('href').startswith('/sport')]

        links = []

        for path in scraper_paths:
          full_url = f"{BASE_URL}/{path}"
          print(full_url)
          links.append(full_url)

        return links


    def get_article_header(self, soup):
        """
        Obtain article header content
        """
        tags=["h1"]
        classes = ["gel-trafalgar-bold qa-story-headline gs-u-mv+", 
                  "ssrcss-rdzqp7-StyledHeading e10rt3ze"]
        scraper = soup.find_all(tags, attrs={'class': classes})
        if len(scraper) > 0:
          header_data = scraper[0].get_text()
        else:
            # get from title
            title_scraper = soup.find_all('title')
            header_data = title_scraper[0].get_text()
        assert header_data is not None
        print(header_data)
        print("\n")
        return header_data


    def get_article_body_and_links(self, soup):
        """
        Obtain article body content
        """
        tags=["p", "h3", "th", "td", "span"]
        classes = ["", "story-body__crosshead", "qa-introduction gel-pica-bold", "gs-o-table__cell",
                 "gs-o-table__cell gs-o-table__cell--bold table__header--bold",
                 "ssrcss-1q0x1qg-Paragraph e1jhz7w10"]

        fixture_classes=["gs-u-display-none gs-u-display-block@m qa-full-team-name sp-c-fixture__team-name-trunc",
                       "sp-c-fixture__number sp-c-fixture__number--away sp-c-fixture__number--ft",
                       "sp-c-fixture__number sp-c-fixture__number--home sp-c-fixture__number--ft"
                       ]
        link_tags = ["a"]
        link_classes = ["story-body__internal-link"]

        link_urls = []

        body_data = []
        for para in soup.find_all(tags, attrs={'class': classes+fixture_classes}):
            text = para.get_text()
            body_data.append(text)
        #print(text)

        links = soup.find_all(link_tags, attrs={'class': link_classes}) # Find all elements with the tag <a>
        for link in links:
            url = link.get("href")
            link_urls.append(url)

        return body_data, link_urls

    def get_content(self, url):
        """
        Download article content - header, followed by body
        """
        print(f"Downloading content from {url}...")
        html_content = requests.get(url).text
        soup = BeautifulSoup(html_content, "html.parser")
        header = self.get_article_header(soup)
        body, links = self.get_article_body_and_links(soup)

        return header, body, links



    def save_content(self, content, filepath):
        """
        Saves content to a file
        """
        print(f"Writing to: {filepath}")
        with open(filepath, 'w') as fp:
            fp.write(content)


    def skip_url(self, url):
        """
        Method that determines when to skip url

        1. If url is already visited
        2. If url is restricted. Restricted urls are:
           https://www.bbc.co.uk/sport/football/66302372 - Link to follow Premier League club
        3. If url is not a BBC football url 

        """
        restricted_urls = [
        "https://www.bbc.co.uk/sport/football/66302372",
        ]
        

        if url in self.visited_urls or url.startswith(tuple(restricted_urls)) \
           or not url.startswith("https://www.bbc.co.uk/sport/football/"):
            print(f"SKIPPING {url}...")
            return True
        else:
            return False

    def download_content(self, url, file_prefix="", level=0):
        """
        Download article content - header, followed by body
        Only recurse 1 level down i.e. follow link in page but not any deeper
        """
        header, body, links = self.get_content(url)

 
        print(f"URL={url}")
        print(f"HEADER={header}")

        filename = header.lower().replace(" ", "_").replace(",","_").replace(":","_").replace("'","")

        content = f"{header}\n".join(body)

        if file_prefix:
            file_prefix += "_"

        filepath = f"{self.destdir}/{file_prefix}{filename}.txt"
        self.save_content(content, filepath)
        self.visited_urls.append(url)

        # Only recurse 1 level deep
        if level > 1:
            return

        print(f"LINKS={links}")

        for link in links:
            if self.skip_url(link):
                continue
            print(f"1. about to download content for {link}")
            file_prefix=os.path.basename(link)
            self.download_content(link, file_prefix, level+1)



    def get_scorelines(self, scoresdata):
        """
         Obtain scorelines from scoresdata list
        """

        print(f"SCORESDATA={scoresdata}")

        size = len(scoresdata)
        ulimit = size
        scorelines = []
        for i in range(0, ulimit, 4):
            j = i+4
            body = scoresdata[i:j]
            print(f"BODY={body}")
            scoreline = f"{body[0]} {body[1]} - {body[2]} {body[3]}"
            print(f"SCORELINE={scoreline}")
            scorelines.append(scoreline)

        return scorelines


    def get_fixture_page_links(self):
        """
          Obtain links to fixture pages
        """
        scores_fixtures_url = "https://www.bbc.com/sport/football/womens-world-cup/scores-fixtures"
        start_date = "2023-07-20"
        end_date = "2023-08-20"
        tournament_dates = pd.date_range(start_date, end_date)
        fixture_links = [f"{scores_fixtures_url}/{dt.date()}" for dt in tournament_dates]
        scores = []
        for link in fixture_links:
            file_prefix = os.path.basename(link)
            header, body, junk = self.get_content(link)
            print(f"H={header} B={body}")

            scorelines = self.get_scorelines(body)

            scores += scorelines

            print(f"SCORES={scores}")
            scores_data = f"{header}\n"
            scores_data += "\n".join(scores)
            filename = header.lower().replace(" ", "_").replace(",","_").replace(":","_").replace("'","")
            filepath = f"{self.destdir}/{filename}.txt"
            self.save_content(scores_data, filepath)



    def retrieve_all_content(self):
        """
         Retrieve all content
        """
        front_page_links = self.scrape_front_page()

        for link in front_page_links:
            if link in self.visited_urls:
                continue
            print(f"2. about to download content for {link}")
            file_prefix = os.path.basename(link)
            self.download_content(link,  file_prefix)

        self.get_fixture_page_links()


def main():
    """ 
    Main function
    """
    scraper = BBCWWCScraper() 

    scraper.retrieve_all_content()

if __name__ == "__main__":
    main()
