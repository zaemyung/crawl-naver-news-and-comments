import scrapy
import uuid
import os
import re
import time
import json
import requests
from datetime import datetime
from datetime import timedelta
import random

class NaverSpider(scrapy.Spider):
    name = "naver"

    def __init__(self, *a, **kw):
        super(NaverSpider, self).__init__(*a, **kw)

    def start_requests(self):
        # 연예 섹션을 제외한 기사들의 주소
        base_url_section = 'http://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&sectionId={}&date={}'
        self.sectionId = {
                100:'default_politics',
                101:'default_economy',
                102:'default_society',
                103:'default_life',
                104:'default_world',
                105:'default_it'
            }
        section_date_format = '%Y%m%d'

        # 연예 섹션 기사들의 주소
        base_url_entertain = 'http://entertain.naver.com/ranking#type=hit_total&date={}'
        entertain_date_format = '%Y-%m-%d'
        
        # 2006 05 01부터 시작하여 하루씩 증가
        start_date = datetime.strptime('20060501', '%Y%m%d')
        delta = timedelta(days=1)
        while(start_date <= datetime.now()):
            section_start_date_str = start_date.strftime(section_date_format)
            entertain_start_date_str = start_date.strftime(entertain_date_format)
            for secId in list(self.sectionId.keys()):
                url = base_url_section.format(secId, section_start_date_str)
                yield scrapy.http.Request(url=url, callback=self.parse_section, meta={'date':section_start_date_str, 'sectionId':secId})
            # yield scrapy.Request(url=base_url_entertain.format(entertain_start_date_str), callback=self.parse_entertain, meta={'date':entertain_start_date_str})
            start_date += delta

    def parse_section(self, response):
        articles = list(set(response.xpath("//ol[@class='ranking_list']/li[contains(@class, 'ranking_item')]")))
        #  print(len(articles))
        for article in articles:
            #  print(article)
            article_url = article.xpath(".//div[@class='ranking_text']/div[@class='ranking_headline']/a/@href").extract_first()
            article_url = response.urljoin(article_url)
            #  print(article_url)
            news_company = article.xpath(".//div[@class='ranking_office']/text()").extract_first()
            #  print(news_company)
            yield scrapy.http.Request(
                    url=article_url, 
                    callback=self.parse_article,
                    meta={'date':response.meta['date'], 'news_company':news_company, 'sectionId':response.meta['sectionId']},
                    headers={
                        'Accept': 'application/json',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Connection': 'keep-alive',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Host': 'www.assetstore.unity3d.com',
                        'Referer': 'https://www.assetstore.unity3d.com/en/',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 '
                                      'Firefox/50.0',
                        'X-Kharma-Version': '0',
                        'X-Requested-With': 'UnityAssetStore',
                        'X-Unity-Session': '26c4202eb475d02864b40827dfff11a14657aa41'
                    },
                    dont_filter=True,
                    errback = self.error_parse
                )

    def parse_entertain(self, response):
        pass

    def error_parse(self, response):
        print("ERROR:", response)
    
    def clean_text(self, text):
        clean = []
        for line in text:
            line = line.strip()
            if 'flash 오류를 우회하기 위한 함수 추가' in line:
                continue
            if len(line) < 1:
                continue
            clean.append(line)
        
        return clean

    def get_emotions(self, ref_url, oid, aid):
        cookies = {
            'NNB': '2O4YAKQTXTRFU',
            'npic': '9V6bf43PJkUhcE3LcetxcSCMqd8JvHq2Sx/WmjD4eHYRKZSWzp7BSRSURWxx0ihaCA==',
            'nid_iplevel': '1',
            'nx_ssl': '2',
            'BMR': 's=1525866338822&r=https%3A%2F%2Fm.blog.naver.com%2FPostView.nhn%3FblogId%3Dcurtate%26logNo%3D20167714225%26proxyReferer%3Dhttps%253A%252F%252Fwww.google.co.kr%252F&r2=https%3A%2F%2Fwww.google.co.kr%2F',
            '_naver_usersession_': 'W14OidZz3xusg1fHD58UQg==',
            'page_uid': 'TYSsUlpwdjNssnJnE9sssssssuV-067828',
        }

        headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
            'Accept': '*/*',
            'Referer': ref_url,
            'Connection': 'keep-alive',
        }

        cur_time = str(int(time.time()*1000))

        params = (
            ('suppress_response_codes', 'true'),
            ('callback', 'jQuery11{}_{}'.format(''.join([str(random.randint(0,9)) for i in range(19)]), cur_time)),
            ('q', 'NEWS[ne_{0}_{1}]|NEWS_SUMMARY[{0}_{1}]|NEWS_MAIN[ne_{0}_{1}]'.format(oid, aid)),
            ('isDuplication', 'false'),
            ('uuid', str(uuid.uuid4())),
            ('_', cur_time),
        )

        response = requests.get('http://news.like.naver.com/v1/search/contents', headers=headers, params=params, cookies=cookies)
        response.encoding = 'utf-8'
        response = json.loads(response.text[46:-2])
        emotions = response['contents'][0]['reactions']
        #  print(emotions)
        return emotions

    def get_comments(self, secId, ref_url, oid, aid):
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,ko;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
            'accept': '*/*',
            'referer': ref_url,
            'authority': 'apis.naver.com',
            'cookie': 'NNB=2O4YAKQTXTRFU; npic=9V6bf43PJkUhcE3LcetxcSCMqd8JvHq2Sx/WmjD4eHYRKZSWzp7BSRSURWxx0ihaCA==; nid_iplevel=1; nx_ssl=2; BMR=s=1525866338822&r=https%3A%2F%2Fm.blog.naver.com%2FPostView.nhn%3FblogId%3Dcurtate%26logNo%3D20167714225%26proxyReferer%3Dhttps%253A%252F%252Fwww.google.co.kr%252F&r2=https%3A%2F%2Fwww.google.co.kr%2F; _naver_usersession_=iHvplbl5ZGyv2jKdsQmdRA==; page_uid=TYn+Ulpp6fwsssmAKBKssssssa0-407427',
        }

        cur_time = str(int(time.time()*1000))
        init_params = (
            ('ticket', 'news'),
            ('templateId', self.sectionId[secId]),
            ('pool', 'cbox5'),
            ('_callback', 'jQuery170{}_{}'.format(''.join([str(random.randint(0,9)) for i in range(17)]), cur_time)),
            ('lang', 'ko'),
            ('country', ''),
            ('objectId', 'news{},{}'.format(oid, aid)),
            ('categoryId', ''),
            ('pageSize', '20'),
            ('indexSize', '10'),
            ('groupId', ''),
            ('listType', 'OBJECT'),
            ('pageType', 'more'),
            ('page', '1'),
            ('initialize', 'true'),
            ('userType', ''),
            ('useAltSort', 'true'),
            ('replyPageSize', '20'),
            ('moveTo', ''),
            ('sort', ''),
            ('includeAllStatus', 'true'),
            ('_', cur_time),
        )

        response = requests.get('https://apis.naver.com/commentBox/cbox/web_neo_list_json.json', headers=headers, params=init_params).json()
        #  print(response)
        if response['success']:
            result = response['result']
            count = response['result']['count']
            pageModel = response['result']['pageModel']
            commentList = response['result']['commentList']

            #  print(count)
            #  print(commentList)
            #  print(pageModel)

            while(response['success'] and pageModel['nextPage'] != 0):
                time.sleep(1)
                prev_commentNo = commentList[0]['commentNo']
                current_commentNo = commentList[-1]['commentNo']
                cur_time = str(int(time.time()*1000))
                next_params = (
                    ('ticket', 'news'),
                    ('templateId', self.sectionId[secId]),
                    ('pool', 'cbox5'),
                    ('_callback', 'jQuery170{}_{}'.format(''.join([str(random.randint(0,9)) for i in range(17)]), cur_time)),
                    ('lang', 'ko'),
                    ('country', ''),
                    ('objectId', 'news{},{}'.format(oid, aid)),
                    ('categoryId', ''),
                    ('pageSize', '20'),
                    ('indexSize', '10'),
                    ('groupId', ''),
                    ('listType', 'OBJECT'),
                    ('pageType', 'more'),
                    ('page', '{}'.format(pageModel['page']+1)),
                    ('refresh', 'false'),
                    ('sort', 'FAVORITE'),
                    ('current', current_commentNo),
                    ('prev', prev_commentNo),
                    ('includeAllStatus', 'false'),
                    ('_', cur_time),
                )

                response = requests.get('https://apis.naver.com/commentBox/cbox/web_neo_list_json.json', headers=headers, params=next_params).json()
                pageModel = response['result']['pageModel']
                commentList = response['result']['commentList']
                result['commentList'].extend(commentList)

        del result['notice']
        del result['config']
        del result['exposureConfig']
        del result['bestList']
        del result['userInfo']

        return result

    def parse_article(self, response):
        #  print("IN parse_article")
        title  = response.xpath("//div[@class='article_info']/h3[@id='articleTitle']/text()").extract_first()
        date = response.xpath("//div[@class='sponsor']/span[@class='t11']/text()").extract_first()
        body = response.xpath("//div[@id='articleBodyContents']//text()").extract()

        rgx_oid_aid = r'oid=(\d+)&aid=(\d+)&'
        rgx_res = re.search(rgx_oid_aid, response.url)
        if rgx_res:
            oid = rgx_res.group(1)
            aid = rgx_res.group(2)

        if title and body:
            body = self.clean_text(body)
            print(title)
            #  print(response.meta['news_company'])
            print(date)
            #  print(body)
            emotions = self.get_emotions(response.url, oid, aid)
            comments = self.get_comments(response.meta['sectionId'], response.url, oid, aid)

            with open(os.path.join('/home1/irteam/users/zaemyung/crawl-naver/crawler/crawler/crawled', response.meta['date']+'.json'), 'a') as outfile:
                a = {
                        'title':title,
                        'date':date,
                        'body':body,
                        'news_company':response.meta['news_company'],
                        'comments':comments,
                        'emotions':emotions
                    }
                json.dump(a, outfile)
                outfile.write('\n')

