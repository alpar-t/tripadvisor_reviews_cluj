# -*- coding: utf-8 -*-
"""
  Define here the models for your scraped items

 See documentation in:
 http://doc.scrapy.org/en/latest/topics/items.html
"""

import scrapy


class AttractionItem(scrapy.Item):
    """ Details of attractions """
    name = scrapy.Field()
    reviewsPage = scrapy.Field()
    number_of_reviews = scrapy.Field()




class ReviewItem(scrapy.Item):
    """ Details of individual reviews """
    attractionName = scrapy.Field()
    ranking = scrapy.Field()
    text = scrapy.Field()
    partial_text = scrapy.Field()
    date = scrapy.Field()
    summary = scrapy.Field()
    reviewer_name = scrapy.Field()
    reviewer_location = scrapy.Field()
    reviewer_reviews = scrapy.Field()
    reviewer_cities = scrapy.Field()
    reviewer_helpfull_votes = scrapy.Field()
