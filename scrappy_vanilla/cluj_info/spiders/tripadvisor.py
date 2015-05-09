# -*- coding: utf-8 -*-
"""
   A Spider that can scrap both list of attractions and review data
"""
import scrapy
from scrapy import log

from cluj_info.items import AttractionItem
from cluj_info.items import ReviewItem

TRIPADVISOR_HOME = "http://www.tripadvisor.com"


class DidTheMarkupChangeOrWhat(Exception):
    """ Exception to indicate that the require infomration could not be extracted from the markup"""


class TripadvisorSpider(scrapy.Spider):
    """ Parse the main attractions and their revies  """
    name = "tripadvisor"
    allowed_domains = ["tripadvisor.com"]
    start_urls = (
        TRIPADVISOR_HOME +
        '/Attractions-g298474-Activities-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
    )

    def parse(self, response):
        self.log("Parsing list of attractions from %s" % response.url, level=log.INFO)

        for section in response.css('.entry'):
            try:
                item = self._parseAttractionFromSection(section)
                yield self._createLocalRequest(
                    item["reviewsPage"],
                    callback=self.parse_reviews,
                    meta_info={'item': item}
                )
            except DidTheMarkupChangeOrWhat, why:
                self.log("Ignoring attraction section: %s" % why)
        else:
            raise DidTheMarkupChangeOrWhat("Can't find any sections for attractions on %s" % response)
        next_page_url = self._attractionsNextPage(response)
        if next_page_url:
            self.log("Found next page of attractions: %s" % next_page_url, level=log.INFO)
            yield self._createLocalRequest(next_page_url)

    def parse_reviews(self, response):
        """ Parse the review pages """
        for section in response.css('div.reviewSelector'):
            try:
                yield self._parseReviewFromSection(section, response.meta['item'])
            except DidTheMarkupChangeOrWhat, why:
                self.log("Ignoring review section: %s" % why)
        else:
            raise DidTheMarkupChangeOrWhat("Can't find any sections for reviews")
        next_page = self._reviewsNextPage(response)
        if next_page:
            yield self._createLocalRequest(
                next_page,
                callback=self.parse_reviews,
                meta_info=response.meta
            )
        else:
            self.log("Reached the end of reviews")

    def _parseAttractionFromSection(self, section):
        item = AttractionItem()
        name = section.xpath('div[@class="property_title"]/a/text()').extract()
        if not name:
            raise DidTheMarkupChangeOrWhat(
                "Attraction section is not laid out as expected, can't make sense of it",
                section.xpath("text()").extract()
            )
        reviewsPage = section.xpath('div[@class="property_title"]/a/@href').extract()
        item["name"] = name[0]
        item["reviewsPage"] = reviewsPage[0]
        return item

    def _parseReviewFromSection(self, section, attractionItem):
        item = ReviewItem()
        item["attractionName"] = attractionItem["name"]
        summary = section.css(".noQuotes").xpath("text()").extract()
        if not summary:
            # not all sections are relevant
            raise DidTheMarkupChangeOrWhat(
               "Review section is not laid out as expected, can;'t make sense of it",
               section.xpath("text()").extract()
            )
        item["partial_text"] = section.css(".partial_entry").xpath("text()").extract()[0]
        item["reviewer_name"] = section.css("span.scrname").xpath("text()").extract()[0]
        item["reviewer_location"] = section.css(".location").xpath("text()").extract()[0]
        item["summary"] = summary[0]
        return item

    def _reviewsNextPage(self, response):
        next_buttons = response.css('a.next').xpath("@href").extract()
        assert len(next_buttons) in [0, 1]
        if next_buttons:
            return next_buttons[0]


    def _attractionsNextPage(self, response):
        next_page_url = [
            x.xpath("@href").extract()[0]
            for x in response.css('#pager_top a')
            if x.xpath("text()").extract()[0] == u'\xbb'
        ]
        assert len(next_page_url) in [0, 1]
        try:
            return next_page_url[0]
        except IndexError:
            return None

    def _createLocalRequest(self, next_page_url, meta_info={}, **kwargs):
        request = scrapy.Request(TRIPADVISOR_HOME + next_page_url, **kwargs)
        request.meta.update(meta_info)
        return request
