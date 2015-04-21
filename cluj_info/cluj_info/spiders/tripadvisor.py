# -*- coding: utf-8 -*-
import scrapy

from cluj_info.items import AttractionItem


class TripadvisorSpider(scrapy.Spider):
    """ Parse the main attractions  """
    name = "tripadvisor"
    allowed_domains = ["tripadvisor.com"]
    start_urls = (
        'http://www.tripadvisor.com/' +
        'Attractions-g298474-Activities-Cluj_Napoca_Cluj_County_Northwest' +
        '_Romania__Transylvania.html',
    )

    def parse(self, response):
        next_page_url = [
            x.xpath("@href").extract()[0]
            for x in response.css('#pager_top a')
            if x.xpath("text()").extract()[0] == u'\xbb'
        ]
        assert len(next_page_url) in [0, 1]
        if next_page_url:
            yield self.make_requests_from_url(
                "http://www.tripadvisor.com" + next_page_url[0])

        for section in response.xpath('//div[@class="entry"]'):
            item = AttractionItem()
            name = section.xpath('div[@class="property_title"]/a/text()').extract()
            if name :
                item["name"] = name
                item["reviewsPage"] = section.xpath('div[@class="property_title"]/a/text()').extract()
                yield item
