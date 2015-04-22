# -*- coding: utf-8 -*-
"""
   A Spider that can scrap both list of attractions and review data
"""
import scrapy

from cluj_info.items import AttractionItem
from cluj_info.items import ReviewItem


class TripadvisorSpider(scrapy.Spider):
    """ Parse the main attractions  """
    name = "tripadvisor"
    allowed_domains = ["tripadvisor.com"]
    start_urls = (
        'http://www.tripadvisor.com/' +
        'Attractions-g298474-Activities-Cluj_Napoca_Cluj_County_Northwest' +
        '_Romania__Transylvania.html',
    )

    def parse_reviews(self, response):
        """ Parse the review pages """
        for section in response.css('div.reviewSelector'):
            item = ReviewItem()
            item["attractionName"] = response.meta['item']["name"][0]
            summary = section.css(".noQuotes").xpath("text()").extract()
            if not summary:
                # not all sections are relevant
                continue
            item["partial_text"] = section.css(".partial_entry").xpath("text()").extract()[0]
            item["reviewer_name"] = section.css("span.scrname").xpath("text()").extract()[0]
            item["reviewer_location"] = section.css(".location").xpath("text()").extract()[0]
            item["summary"] = summary[0]
            yield item
        if response.css('a.next'):
            request = scrapy.Request(
                "http://www.tripadvisor.com" +
                response.css('a.next').xpath("@href").extract()[0],
                callback=self.parse_reviews
            )
            request.meta['item'] = response.meta["item"]
            yield request

    def parse(self, response):
        next_page_url = [
            x.xpath("@href").extract()[0]
            for x in response.css('#pager_top a')
            if x.xpath("text()").extract()[0] == u'\xbb'
        ]
        assert len(next_page_url) in [0, 1]
        if next_page_url:
            yield scrapy.Request(
                "http://www.tripadvisor.com" + next_page_url[0])

        for section in response.xpath('//div[@class="entry"]'):
            item = AttractionItem()
            name = section.xpath(
                'div[@class="property_title"]/a/text()').extract()
            reviewsPage = section.xpath(
                'div[@class="property_title"]/a/@href').extract()
            if name:
                item["name"] = name[0]
                item["reviewsPage"] = reviewsPage[0]
                request = scrapy.Request(
                    "http://www.tripadvisor.com" + reviewsPage[0],
                    callback=self.parse_reviews
                )
                request.meta['item'] = item
                yield request
