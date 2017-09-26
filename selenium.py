#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime
from datetime import timedelta
from selenium import webdriver

driver = webdriver.Chrome('./chromedriver')
driver.implicitly_wait(5)

# 주간 댓글 최다 기사 ~50건
base_url_temp = 'http://news.naver.com/main/ranking/memoWeek.nhn?rankingType=memo_week&sectionId=000&date={}'
# 2005.06.11부터 데이터가 있음
start_date = datetime.strptime('20050615', '%Y%m%d')
delta = timedelta(days=7)
while(start_date <= datetime.now()):
    start_date_str = start_date.strftime('%Y%m%d')
    base_url = base_url_temp.format(start_date_str)
    start_date += delta
    driver.get(base_url)
    articles = driver.find_elements_by_xpath("//div[@class='content']//a[contains(@href, '/main/ranking/read.nhn?') and not(ancestor::div[@class='thumb'])]")
    print(articles)
    raw_input()
