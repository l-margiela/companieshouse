# -*- coding: utf-8 -*-
import scrapy, re

from companieshouse.items import OfficerItem
from urlparse import urlparse

class CompanieshouseSpider(scrapy.Spider):
    def __init__(self, domain=None, query=""):
        name = "companieshouse"
        allowed_domains = ["beta.companieshouse.gov.uk"]
        start_urls = ["https://beta.companieshouse.gov.uk/search/officers?q=" + query]

    def parse(self, response):
        uri = urlparse(response.url)
        for sel in response.xpath('//main/div[@class="column-full-width"]/div[@class="grid-row"]/div/article[@id="services-information-results"]/ul/li'):
            yield scrapy.Request(uri.scheme + "://" + uri.netloc + sel.xpath('h3/a/@href').extract(), callback=self.officer_parse)

    def officer_parse(self, response):
        officer = OfficerItem()

        full_name = re.search('(.+) ([A-Z]+)', response.xpath('//main/header/h1/text()').extract()[0])
        officer["name"] = full_name.group(1)
        officer["surname"] = full_name.group(2).title()

        for sel in response.xpath('//main/div[@class="appointments"]/div[@class="appointments-list"]/div'):
            company = CompanieshouseItem()

            name_and_crn = r.search('(.+) \(([0-9A-Z]+)\)', sel.xpath('h2/a/text()').extract()[0])
            comapny["name"] = name_and_crn.group(1)
            company["crn"] = name_and_crn.group(2)

            company["address"] = sel.xpath('div[@class="grid-row"][1]/dl[@class="column-two-thirds"]/dd/text()').extract()
