import json
from scrapy.spiders import CrawlSpider
from scrapy import Request
import re
import html2text
from datetime import datetime
import pandas as pd

class NaukriJDSpider(CrawlSpider):
    name = "naukri_jd"
    allowed_domains = ["www.naukri.com"]
    
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0',

    # Skill Search URL
    search_key_words = ['data-scientist', 'data-engineer', 'data-analyst',
    'big-data-engineer', 'python-developer']
    base_url = "https://www.naukri.com/jobapi/v3/search?"
    noOfResult = "100"
    urlType='search_by_keyword'
    searchType='adv'
    keyword = ", ".join(search_key_words)
    seoKey =  "-".join(search_key_words)
    src="jobsearchDesk"
    latLong=""
    pageNo = 1
    search_urls = []
    
    # JD BASE URL
    jd_base_url = "https://www.naukri.com/jobapi/v4/job/"
    
    # Starting URL
    start_urls = ["https://www.naukri.com/browse-jobs",]

    # DATAFRAME
    now = datetime.now()
    now = now.strftime("%m_%d_%Y-%H_%M_%S")
    result = pd.DataFrame()

    def start_requests(self):
        headers= {'User-Agent': self.USER_AGENT}
        for url in self.start_urls:
            print(url)
            yield Request(url, headers=headers, callback=self.submit_form)
            
    def submit_form(self,response):
        # Hidden Value
        app_id = response.xpath('//*[@id="qsbForm"]/div[1]/input[1]/@value')
        self.app_id_value = app_id.extract_first()

        # Cookie
        # cookie = response.headers.getlist('Set-Cookie')#[1].decode('utf-8')
        # cookie = " ".join(map(lambda x : x.decode('utf-8'),cookie))
        # print(f"COOKIE: {cookie}")

        # # Header
        self.form_header = {
            "User-Agent": self.USER_AGENT,
            "scheme" : "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"97\", \"Chromium\";v=\"97\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "referrer": "https://www.naukri.com/browse-jobs",
            "referrerPolicy": "strict-origin-when-cross-origin",
            'appid' : self.app_id_value,
            'systemid' : self.app_id_value,
        }

        for i in range(1,101):
            url = f"{self.base_url}noOfResult={self.noOfResult}&urlType={self.urlType}&searchType={self.searchType}&pageNo={self.pageNo}&sort=r&keyword={self.keyword}&seoKey={self.seoKey}&src={self.src}&latLong={self.latLong}"
            self.search_urls.append(url)
            yield Request(
            url,
            headers=self.form_header,
            method='GET',
            callback=self.parse
            )
            self.pageNo += 1

    def parse(self,response):
        # print("Inside Parse:")
        print(response.url)
        print(response.status)
        json_response = json.loads(response.text)

        # with open(f"./data/base_jd_{str(self.pageNo)}.json", "w") as file:
	    #     json.dump(json_response, file)

        jd_ids = map(lambda x : x['jobId'], json_response['jobDetails'])
        jd_urls = list(map(lambda id : f"{self.jd_base_url}{id}",jd_ids))
        print("Total URLS: ",len(jd_urls))
        for url in jd_urls:
            yield Request(
                url,
                headers=self.form_header,
                callback=self.get_jds
            )


    def get_jds(self,response):
        id = response.url.split("/")[-1]
        json_response = json.loads(response.text)

        # with open(f"./data/JD/{id}.json", "w") as file:
	    #     json.dump(json_response, file)
        
        title = json_response['jobDetails']['title']
        jd = json_response['jobDetails']['description']
        jd = self.fn_clean_text(jd)

        self.result = self.result.append({
            'title' : title,
            'job_description' : jd
        },ignore_index=True)
        self.result.to_csv(f"./data/{self.now}_.csv",index=False)


    def fn_clean_text(self,text):
        try:
            text = html2text.html2text(text)
            text = re.sub("\*"," ",text)
            text = re.sub("\s{2,}"," ",text)
            return re.sub("\n",".\n",text).strip()
        except:
            return text