from html.parser import HTMLParser
import urllib.request
import re
from urllib.parse import urlparse
from collections import deque
import os
from bs4 import BeautifulSoup
import requests

# 정규화
HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'

class HyperlinkParser(HTMLParser):
  def __init__(self):
    super.__init__()
    self.hyperlinks = []  # 하이퍼링크를 저장할 목록

  # 재정의
  def handle_starttag(self, tag, attrs):
    attrs = dict(attrs)
    # 태그가 a 태그이고 href 속성이 있는 경우 href 속성을 하이퍼링크 목록에 추가
    if tag == 'a' and 'href' in attrs:
      self.hyperlinks.append(attrs['href'])

###############################################################################
#    get_hyperlinks
#    URL을 인수로 받고, URL을 열고, HTML 콘텐츠를 읽습니다. 
#    그런 다음, 해당 페이지에서 발견된 모든 하이퍼링크를 반환합니다.
#   return : [] > hyperlinks
###############################################################################
def get_hyperlinks(url):
  try:
    with urllib.request.urlopen(url) as response:
      # 응답이 html 이 아니면 리턴
      if not response.info().get('Content-Type').startswith("text/html"):
        return []
      
      html = response.read().decode('utf-8')
  except Exception as e:
    print(e)
    return []
  
  parser = HyperlinkParser()
  parser.feed(html)
  
  return parser.hyperlinks


###############################################################################
#    get_domain_hyperlinks
#    내가 정한 웹의 도메인만 색인하는 것
#   return : [] > clean links
###############################################################################
def get_domain_hyperlinks(local_domain, url):
  clean_links = []
  for link in set(get_hyperlinks(url)):
    clean_link = None

    if re.search(HTTP_URL_PATTERN, link):
      # URL 을 구문 분석하고 도메인지 동일한지 확인
      url_obj = urlparse(link)
      if url_obj.netloc == local_domain:
        clean_link = link
      else: # 링크가 URL이 아닌 경우 상대 링크인지 확인
        if link.startswith("/"):
          link = link[1:]
        elif link.startswith("#") or link.startswith("mailto:"):
          continue
        clean_link = "https://" + local_domain + "/" + link

      if clean_link is not None:
        if clean_link.endswith("/"):
          clean_link = clean_link[:-1]
        clean_links.append(clean_link)

  return list(set(clean_links))


###############################################################################
#    crawl
#    크롤링
###############################################################################
def crawl(url):
  local_domain = urlparse(url).netloc
  queue = deque([url]) # 크롤링할 URL을 저장할 대기열을 만든다
  seen = set([url]) # 이미 본 URL을 저장하기 위한 세트를 생성합니다(중복 없음)

  if not os.path.exists("text/"):
    os.mkdir("text/")

  if not os.path.exists(f"text/{local_domain}/"):
    os.mkdir(f"text/{local_domain}/")

  if not os.path.exists("processed"):
    os.mkdir("processed")

  while queue: #대기열이 비어 있지 않은 동안 크롤링을 계속합니다.
    url = queue.pop()
    print(url)

    try:
      with open(f'text/{local_domain}/{url[8:].replace("/", "_")}.txt', "w", encoding='utf-8') as f:
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        text = soup.get_text()
        # You need to enable JavaScript to run this app. 있으면 크롤링을 중지
        if ("You need to enable JavaScript to run this app." in text):
          print(f"Unable to parse page {url} due to JavaScript being required")

        f.write(text)
    except Exception as e:
      print("Unable to parse page " + url)

    # URL에서 하이퍼링크를 가져와 대기열에 추가합니다.
    for link in get_domain_hyperlinks(local_domain, url):
      if link not in seen:
        queue.append(link)
        seen.add(link)