import scrapy
import os
import re
import json
from datetime import datetime
from datetime import timedelta

class NaverSpider(scrapy.Spider):
    name = "naver"

    def __init__(self, *a, **kw):
        super(NaverSpider, self).__init__(*a, **kw)

    def start_requests(self):
        # 연예 섹션을 제외한 기사들의 주소
        base_url_section = 'http://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&sectionId={}&date={}'
        sectionId = {
                100:'정치',
                101:'경제',
                102:'사회',
                103:'생활/문화',
                104:'세계',
                105:'IT/과학'
                }
        section_date_format = '%Y%m%d'

        # 연예 섹션 기사들의 주소
        base_url_entertain = 'http://entertain.naver.com/ranking#type=hit_total&date={}'
        entertain_date_format = '%Y-%m-%d'
        
        # 2006 03 30부터 시작하여 하루씩 증가
        start_date = datetime.strptime('20060330', '%Y%m%d')
        delta = timedelta(days=1)
        while(start_date <= datetime.now()):
            section_start_date_str = start_date.strftime(section_date_format)
            entertain_start_date_str = start_date.strftime(entertain_date_format)
            for secId in list(sectionId.keys()):
                url = base_url_section.format(secId, section_start_date_str)
                yield scrapy.Request(url=url, callback=self.parse_section, meta={'date':section_start_date_str})
                input()
            # yield scrapy.Request(url=base_url_entertain.format(entertain_start_date_str), callback=self.parse_entertain, meta={'date':entertain_start_date_str})
            start_date += delta

    def parse_section(self, response):
        articles = list(set(response.xpath("//ol[@class='ranking_list']/li[contains(@class, 'ranking_item')]").extract()))
        print(articles)
        #  for article in articles:
        #      article_url = article.xpath("//div[@class='ranking_headline']/a[contains(@href, '/main/ranking/read.nhn?')]/@href").extract_first()
        #      print(article_url)
        #      news_company = article.xpath("//div[@class='ranking_office']/text()").extract_first()
        #      print(news_company)
        #      #  yield scrapy.Request(url=response.urljoin(article_url), \
        #      #          callback=self.parse_article, meta={'date':response.meta['date'], 'news_company':news_company})

    def parse_entertain(self, response):
        pass
    
    def clean_text(self, text):
        cleaned_text = re.sub('[a-zA-Z]', '', text)
        cleaned_text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]','', cleaned_text)
        
        return cleaned_text

    def parse_article(self, response):
        title  = response.xpath("//div[@class='article_info']/h3[@id='articleTitle']/text()").extract_first()
        date = response.xpath("//div[@class='sponsor']/span[@class='t11']/text()").extract_first()
        body = response.xpath("//div[@id='articleBodyContents']/text()").extract()
        body = self.clean_text(body)

        with open(response.meta['week']+'.json', 'a') as outfile:
            a = {
                    'title':title,
                    'date':date,
                    'body':body
                }
            json.dump(a, outfile)

