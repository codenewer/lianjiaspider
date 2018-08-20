import requests
from downloader import Downloader
from lxml.html import fromstring,tostring
import json
from multiprocessing import Process,queues
import time
import threading

class scrapyProcess(Process):

    def __init__(self,region,q,agent,proxies):
        #实现父类构造函数
        Process.__init__(self)
        self.region = region
        self.q = q
        self.agent =agent
        self.proxies =proxies

    def run(self):
        starturl = 'https://nj.lianjia.com/chengjiao/' + self.region+'/'
        D = Downloader(user_angent=self.agent,proxies=self.proxies)
        self.seen = set()
        self.q.append(starturl)
        while self.q:
            url = self.q.pop()
            html = D(url)
            if html:
                totalpages = self.scrapy_page(html)
                if totalpages:
                    for page in range(2,totalpages):
                        urlpage = starturl+'/'+"pg"+str(page)+"/"
                        if urlpage not in self.seen:
                            self.seen.add(urlpage)
                            self.q.append(urlpage)
                            htmlpage = D(urlpage)
                            links = self.scrapy_callback(htmlpage)
                            for linkurl in links:
                                if linkurl not in self.seen:
                                    self.seen.add(linkurl)
                                    self.q.append(linkurl)
                else:
                    print(url)
                    links = self.scrapy_callback(html)
                    for linkurl in links:
                        if linkurl not in self.seen:
                            self.seen.add(linkurl)
                            self.q.append(linkurl)
            else:
                continue


    #获取新的成交房源url并且存储数据
    def scrapy_callback(self,html):
        tree = fromstring(html)
        links = []
        title = tree.xpath('//div[@class="house-title LOGVIEWDATA LOGVIEW"]/div/text()')
        price = tree.xpath('//span[@class="dealTotalPrice"]/i/text()')

    #插入数据库房子的信息
        try:
            print(title)
            with open('lianjia.txt','a') as f:
                f.writelines(title + price)
        finally:
            if f:
                f.close()

        link = tree.xpath('//a[@class="img"]/@href')
        link2= tree.xpath('//div[@class="fl pic"]/a/@href')
        if link:
            for li in link:
                links.append(li)
        if link2:
            for li2 in link2:
                links.append(li2)
        return links
    #构建爬取队列

    def scrapy_page(self, html):
        tree = fromstring(html)
        pagejson = tree.xpath('//div[@class="page-box house-lst-page-box"]/@page-data')
        totalpage=0
        if pagejson:
            pagejson = json.loads(pagejson[0])
            totalpage = pagejson["totalPage"]
        return totalpage

if __name__ == '__main__':
    #多进程
    q = []
    regions = ["gulou","jianye"]
    process_list = []
    start = time.time()
    for region in regions:
        scrapySpider = scrapyProcess(region,q,"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0",None)
        scrapySpider.start()
        process_list.append(scrapySpider)
    for pro in process_list:
        pro.join()
    print ("耗时:%s"%time.time()-start)
        #串行
        #scrapyItem("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0",None)