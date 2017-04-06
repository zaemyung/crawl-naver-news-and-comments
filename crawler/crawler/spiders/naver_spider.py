import scrapy
import os
import json

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
        
        # 20050622부터 시작하여 일주일씩 증가
        start_date = 20050622

        # TODO FROM HERE
        for year in years:
            url = base_url+str(year)+'.html'
            yield scrapy.Request(url=url, callback=self.parse_year)

    def parse_year(self, response):
        days = response.xpath("//p/a[starts-with(@href, \
                              '/resources/archive/us/')]")
        for day in days:
            day_url = day.xpath('@href').extract_first()
            date = day_url.split("/")[-1][:-5] # e.g. 20160130
            item = {'date':date}
            yield scrapy.Request(url=response.urljoin(day_url), \
                                 callback=self.parse_day, meta={'item':item})

    def parse_day(self, response):
        articles = response.xpath("//div/a[starts-with(@href, \
                              'http://www.reuters.com/article/')]")
        for article in articles:
            article_link = article.xpath("@href").extract_first()
            article_title = article.xpath("text()").extract_first()
            item = response.meta['item']
            item['title'] = article_title
            yield scrapy.Request(url=response.urljoin(article_link), \
                                 callback=self.parse_article, \
                                 meta={'item':item})

    def parse_article(self, response):
        item = response.meta['item']
        section = response.xpath("//span[@class='article-section']\
                                 /a/text()").extract_first().replace(" ", "_")
        texts = response.xpath("//*[@id='article-text']/p/text()").extract()
        date = item['date']
        direc = date[:4]+"/"+date[4:6]+"/"
        save_path = "./crawled/"+direc # e.g. ./crawled/2011/02
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        with open(os.path.join(save_path, date[-2:]+".json"), 'a') as out_file:
            article = {
                        'title':item['title'], 'section':section,
                        'date':date, 'text':texts
                      }
            out = json.dumps(article)
            out_file.write(out+"\n")
