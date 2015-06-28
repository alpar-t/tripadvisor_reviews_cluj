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
    start_urls = [
        TRIPADVISOR_HOME + x for x in (
            '/Attractions-g298474-Activities-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            # manual work around for the groups that show up above, and require a click to get to
            # these are loaded with JS so not as straight forward to walk with the crawler
            '/Attractions-g298474-Activities-c56-t110-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c56-t208-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c56-t261-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c61-t214-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c26-t144-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c61-t263-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c42-t225-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c42-t139-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c40-t127-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html',
            '/Attractions-g298474-Activities-c58-t111-Cluj_Napoca_Cluj_County_Northwest_Romania_Transylvania.html'
        )
    ]

    def parse(self, response):
        self.log("Parsing list of attractions from %s" % response.url, level=log.INFO)

        atLeastOneFound = False
        for section in response.css('.entry'):
            try:
                item = self._parseAttractionFromSection(section)
                atLeastOneFound = True
                yield self._createLocalRequest(
                    item["reviewsPage"],
                    callback=self.parse_reviews,
                    meta_info={'item': item}
                )
            except DidTheMarkupChangeOrWhat, why:
                self.log("Ignoring attraction section: %s" % why)
        if not atLeastOneFound:
            raise DidTheMarkupChangeOrWhat("Can't find any sections for attractions on %s" % response)
        next_page_url = self._attractionsNextPage(response)
        if next_page_url:
            self.log("Found next page of attractions: %s" % next_page_url, level=log.INFO)
            yield self._createLocalRequest(next_page_url)

    def parse_reviews(self, response):
        """ Parse the review pages """
        atLeastOneFound = False
        for section in response.css('div.reviewSelector'):
            try:
                atLeastOneFound = True
                #if [ x for x in  section.xpath("text()").extract() if x.strip() ]:
                yield self._parseReviewFromSection(section, response.meta['item'])
                #else:
                #    self.log("Found and empty review section, will ignore it", level=log.DEBUG)
            except DidTheMarkupChangeOrWhat, why:
                self.log("Ignoring review on %s: %s" % (response.url, why), log=log.ERROR)
        if not atLeastOneFound:
            if "Be the first to share your experiences!" in response.css("body").extract()[0]:
                self.log("Doesn't seem to have any reviews")
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
            # no sure why this sometimes comes back with a different format...
            summary = section.css(".taLnk").xpath("text()").extract()
            if not summary:
                raise DidTheMarkupChangeOrWhat(
                    "Review section is not laid out as expected, can't make sense of it",
                    section.extract()
                )
        item["partial_text"] = section.css(".partial_entry").xpath("text()").extract()[0]
        fielmap = {
            "reviewer_name": "span.scrname",
            "reviewer_location": ".location",
            "date": ".ratingDate",
            "reviewer_reviews": ".badgeText"
        }
        for key, selector in fielmap.items():
            try:
                item[key] = section.css(selector).xpath("text()").extract()[0]
            except IndexError:
                item[key] = "unknonw"
        item["date"] =  item["date"].replace("Reviewed", "").strip()
        item["reviewer_reviews"] =  item["reviewer_reviews"].replace("reviews", "").strip().split(" ")[0].split(" ")[0]
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
