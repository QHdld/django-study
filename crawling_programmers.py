import requests
import time
import random
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter as MarkdownifyConverter
from selenium import webdriver
from selenium.webdriver.common.by import By

class BasicSelector:
    def select_level():
        level_inputted = int(input("원하는 문제의 레벨을 입력하세요(0~5):"))
        if 0<=level_inputted<=5:
            level = "&levels=" + str(level_inputted)
        else:
            level = ""
            print("")
        return level

    def select_language():
        language_inputted = input("원하는 문제의 언어를 입력하세요:")
        if language_inputted in ["c", "cpp", "csharp", "go", "java", "javascript", "kotlin", "python2", "python3", "ruby", "scala", "swift", "mysql", "oracle"]:
            language = "&languages=" + language_inputted
        else:
            language = ""
        return language

class TestSelector:
    def select_test(self):
        test_number = input("문제 번호를 입력하세요:")
        problem_page_url = f"https://school.programmers.co.kr/learn/courses/30/lessons/{test_number}"
        return problem_page_url

class TestCrawler:
    def __init__(self, problem_page_url, parser):
        self.request_html(problem_page_url)
        self.convert_html_bs4(parser)
        self.parse()

    def request_html(self, problem_page_url):
        response = requests.get(problem_page_url)
        self.html = response.text

    def convert_html_bs4(self, parser):
        self.soup = BeautifulSoup(self.html, parser)

    def parse(self):
        category, title, description= self.find_category_title()

    def find_category_title(self):
        category_title_soup = self.soup.find("ol", "breadcrumb")
        _, category_soup, title_soup = category_title_soup.find_all("li")
        category = category_soup.get_text()
        title = title_soup.get_text()
        description = md(self.soup.find("div", "guide-section-description"))
        print(category, title, description)
        return category, title, description

def md(soup, **options):
    return MarkdownifyConverter(**options).convert_soup(soup)

if __name__ == "__main__":
    # parser = "lxml"
    # url = "https://school.programmers.co.kr/learn/challenges?order=acceptance_desc&page=1"
    # level = BasicSelector.select_level()
    # language = BasicSelector.select_language()
    # select_url = f"https://school.programmers.co.kr/learn/challenges?order=recent{level}{language}"
    # selector = TestSelector()
    # problem_page_url = selector.search_test()
    # crawler = TestCrawler(problem_page_url, parser)

    # 사용자 입력을 받아 레벨과 언어 선택
    level = BasicSelector.select_level()
    language = BasicSelector.select_language()

    # URL 구성
    url = "https://school.programmers.co.kr/learn/challenges?order=acceptance_desc&page=1"
    select_url = f"https://school.programmers.co.kr/learn/challenges?order=recent{level}{language}"
    
    # 문제 선택
    parser = "lxml"
    problem_page_url = TestSelector().select_test()

    # 문제 페이지 크롤링
    test_crawler = TestCrawler(problem_page_url, parser)
    
    # 파싱된 결과 출력
    category, title, description = test_crawler.parse()
    print("Category:", category)
    print("Title:", title)
    print("Description:", description)
