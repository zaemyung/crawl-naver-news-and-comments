#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import requests
from bs4 import BeautifulSoup as bs
import time

def crawl_article(driver, article_url):
    xpaths = {
        'enter':{
            'title':"//h2[@class='end_tit']",
            'date':"//div[@class='article_info']/span[@class='author']//em",
            'content':"//div[@id='articeBody']"
        },
        'sports':{
            'title':"//div[@class='news_headline']//h4[@class='title']",
            'date':"//div[@class='news_headline']/div[@class='info']/span",
            'content':"//div[@id='newsEndContents']"
        },
        'else':{
            'title':"//h3[@id='articleTitle']",
            'date':"//div[@class='sponsor']/span[@class='t11']",
            'content':"//div[@id='articleBodyContents']"
        }
    }
    def parse_article(cat):
        title = driver.find_element_by_xpath(xpaths[cat]['title']).text
        date = driver.find_element_by_xpath(xpaths[cat]['date']).text
        content = driver.find_element_by_xpath(xpaths[cat]['content']).text
        print(title)
        print(date)
        print(content)

    driver.get(article_url)
    wait(3)
    article_url = driver.current_url
    print('real url:', article_url)
    if 'entertain.naver.com' in article_url:
        parse_article('enter')
    elif 'sports.news.naver.com' in article_url:
        parse_article('sports')
    else:
        parse_article('else')

def wait(n):
    print("Waiting for {} seconds...".format(n))
    time.sleep(n)
    print("Up!")

def main():
    driver = webdriver.Chrome('./chromedriver')
    driver.implicitly_wait(10)

    # 주간 댓글 최다 기사 ~50건
    weekly_url_temp = 'http://news.naver.com/main/ranking/memoWeek.nhn?rankingType=memo_week&sectionId=000&date={}'
    # 2005.06.11부터 데이터가 있음
    start_date = datetime.strptime('20170615', '%Y%m%d')
    delta = timedelta(days=7)
    while(start_date <= datetime.now()):
        start_date_str = start_date.strftime('%Y%m%d')
        weekly_url = weekly_url_temp.format(start_date_str)
        start_date += delta
        driver.get(weekly_url)
        articles = driver.find_elements_by_xpath("//div[@class='content']//a[contains(@href, '/main/ranking/read.nhn?') and not(ancestor::div[@class='thumb'])]")
        articles_urls = [a.get_attribute('href') for a in articles]
        # print(articles_urls)
        for a_url in articles_urls:
            print(a_url)
            crawl_article(driver, a_url)
            raw_input('Wating for ENTER to continue')
            wait(3)
        raw_input('Wating for ENTER to continue')
        wait(3)


if __name__ == '__main__':
    main()