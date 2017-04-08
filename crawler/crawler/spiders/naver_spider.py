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
        # base_url_section+sectionId+base_url_date+YYYYMMDD
        base_url_section = 'http://news.naver.com/main/ranking/memoWeek.nhn?rankingType=memo_week&sectionId='
        base_url_date = '&date='
        sectionId = {
                100:'정치',
                101:'경제',
                102:'사회',
                103:'생활/문화',
                104:'세계',
                105:'IT/과학'
                }
        # 연예 섹션 기사들의 주소
        # base_url_entertain+YYYYMMDD
        base_url_entertain = 'http://entertain.naver.com/ranking/memo?date='
        
        # 20050615부터 시작하여 일주일씩 증가
        start_date = datetime.strptime('20050615', '%Y%m%d')
        delta = timedelta(days=7)
        while(start_date <= datetime.now()):
            start_date_str = start_date.strftime('%Y%m%d')
            for secId in list(sectionId.keys()):
                url = base_url_section+str(secId)+base_url_date+start_date_str
                yield scrapy.Request(url=url, callback=self.parse_section, meta={'week':start_date_str})
            # yield scrapy.Request(url=base_url_entertain+start_date_str, callback=self.parse_entertain, meta={'week':start_date_str})
            start_date += delta

    def parse_section(self, response):
        articles = set(response.xpath("//div[@class='content']//a[contains(@href, '/main/ranking/read.nhn?')]/@href").extract())
        for article in articles:
            yield scrapy.Request(url=response.urljoin(article), \
                                 callback=self.parse_article, meta={'week':response.meta['week']})

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

