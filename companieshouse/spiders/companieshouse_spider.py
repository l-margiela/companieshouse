import scrapy, re

from companieshouse.items import CompanieshouseItem, OfficerItem
from urlparse import urlparse

class CompanieshouseSpider(scrapy.Spider):
    name = "companieshouse"
    allowed_domains = ["beta.companieshouse.gov.uk"]
    start_urls = ["https://beta.companieshouse.gov.uk/officers/eYKVcUJujkKZPwW0R6P16Tu6cmI/appointments"]

    def parse(self, response):
        uri = urlparse(response.url)
        for sel in response.xpath('//main[@id="page-container"]/div[@class="appointments"]/div[@class="appointments-list"]/div'):
            name_and_cnr = re.search('(.+) \(([0-9A-Z]+)\)', sel.xpath('h2[1]/a/text()').extract()[0])
            item = CompanieshouseItem()
            item["company_name"] = name_and_cnr.group(1)
            item["cnr"] = name_and_cnr.group(2)
            item["address"] = sel.xpath('div[@class="grid-row"][1]/dl[@class="column-two-thirds"]/dd/text()').extract()[0].strip()
            item["officers"] = []

            officers_request = scrapy.Request(uri.scheme + "://" + uri.netloc + "/company/" + item["cnr"] + "/officers", callback=self.officers_parse)
            officers_request.meta["item"] = item
            yield officers_request

            try:
                next_page = response.xpath('//*[@id="next-page"]/@href').extract()[0]
                if next_page:
                    yield scrapy.Request(uri.scheme + '://' + uri.netloc + next_page, self.parse)
            except IndexError:
                pass

    def officers_parse(self, response):
        for sel in response.xpath('//main/div[@class="appointments-list"]/div'):
            officer = OfficerItem()

            full_name = sel.xpath('h2/span/a/text()').extract()[0]
            try:
                name = re.search('([A-Z]+), ([a-zA-Z]+).*', full_name)
                officer["name"] = name.group(2).title()
                officer["surname"] = name.group(1).title()
            except:
                officer["name"] = full_name

            try:
                officer["nationality"] = sel.xpath('div[@class="grid-row"][2]/dl[1]/dd/text()').extract()[0].strip()
            except IndexError:
                pass

            officer["address"] = sel.xpath('dl[1]/dd/text()').extract()[0].strip()

            response.meta["item"]["officers"].append(dict(officer))
        return response.meta["item"]
