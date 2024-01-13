
"""

webscrape_bbc_wwc2023.py
Script that scrapes  BBC Women's World Cup 2023 site for article content

https://www.bbc.com/sport/football/womens-world-cup


"""

from bs4 import BeautifulSoup
import pandas as pd
import requests
import os


FRONT_PAGE_URL = "https://www.bbc.com/sport/football/womens-world-cup"
BASE_URL = "https://www.bbc.com"
SCORES_FIXTURES_URL = "https://www.bbc.com/sport/football/womens-world-cup/scores-fixtures"


def scrape_front_page():
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

front_page_links = scrape_front_page()

def get_article_header(soup):
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

def get_article_body(soup):
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
  body_data = []
  for para in soup.find_all(tags, attrs={'class': classes+fixture_classes}):
  #for para in soup.find_all("p"):
    text = para.get_text()
    body_data.append(text)
    #print(text)
  return body_data




def get_content(url):
  """
  Download article content - header, followed by body
  """
  print(f"Downloading content from {url}...")
  html_content = requests.get(url).text
  soup = BeautifulSoup(html_content, "html.parser")
  header = get_article_header(soup)
  body = get_article_body(soup)
  return header, body

def save_content(content, filepath):
  """
  Saves content to a file
  """
  print(f"Writing to: {filepath}")
  with open(filepath, 'w') as fp:
    fp.write(content)

def download_content(url, destdir, file_prefix=""):
  """
  Download article content - header, followed by body
  """
  header, body = get_content(url)

  filename = header.lower().replace(" ", "_").replace(",","_").replace(":","_").replace("'","")

  content = f"{header}\n".join(body)

  if file_prefix:
    file_prefix += "_"

  filepath = f"{destdir}/{file_prefix}{filename}.txt"
  save_content(content, filepath)





def get_scorelines(scoresdata):
  """
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


def get_fixture_page_links(destdir):
  """
  """
  scores_fixtures_url = "https://www.bbc.com/sport/football/womens-world-cup/scores-fixtures"
  start_date = "2023-07-20"
  end_date = "2023-08-20"
  tournament_dates = pd.date_range(start_date, end_date)
  fixture_links = [f"{scores_fixtures_url}/{dt.date()}" for dt in tournament_dates]
  scores = []
  for link in fixture_links:
      file_prefix = os.path.basename(link)
      header, body = get_content(link)
      print(f"H={header} B={body}")

      scorelines = get_scorelines(body)

      scores += scorelines

  print(f"SCORES={scores}")
  scores_data = f"{header}\n"
  scores_data += "\n".join(scores)
  filename = header.lower().replace(" ", "_").replace(",","_").replace(":","_").replace("'","")
  filepath = f"{destdir}/{filename}.txt"
  save_content(scores_data, filepath)



#get_fixture_page_links()

def retrieve_all_content():
  """
  """

  destdir = "/tmp/wwc2023"

  front_page_links = scrape_front_page()

  for link in front_page_links:
      file_prefix = os.path.basename(link)
      download_content(link, destdir, file_prefix)

  get_fixture_page_links(destdir)


def main():
    """ 
    Main function
    """
    retrieve_all_content()

if __name__ == "__main__":
    main()
