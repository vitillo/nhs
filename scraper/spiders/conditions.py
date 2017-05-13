import scrapy
import re
import functools
import string


def _to_ascii(text):
    return text.encode("utf-8").replace("\xa0", " ").decode("ascii", "ignore")


class QuotesSpider(scrapy.Spider):
    name = "conditions"

    def start_requests(self):
        for char in string.ascii_lowercase:
            self.log("Processing directory \"{}\"".format(char))
            url = "http://www.nhs.uk/Conditions/Pages/BodyMap.aspx?Index={}".format(char)
            yield scrapy.Request(url=url, callback=self.parse_directory)

    def parse_directory(self, response):
        conditions = response.xpath('//a/@href').re('^/[cC]onditions\/[^/]*$')
        self.log("Found {} conditions".format(len(conditions)))

        for condition in conditions:
            yield scrapy.Request(url=response.urljoin(condition),
                                 callback=functools.partial(self.parse_condition, condition.lower()))

    def parse_condition(self, condition, response):
        title = _to_ascii(response.xpath("//h1/text()").extract()[0])
        text = "".join(response.xpath("//div[contains(@class, 'main-content') or contains(@class, 'article')]/descendant-or-self::*[not(self::script)]/text()").extract())
        text = re.sub("\n|\t|\s\s+", " ", _to_ascii(text))

        yield {
          "url": response.url,
          "title": title,
          "text": text
        }

        links = response.xpath('//a/@href').extract()

        for link in links:
            link = link.lower()

            if re.search("clinical-trial|community|savefavourite", link):
                continue

            if not re.match("{}/.*".format(condition), link):
                continue

            yield scrapy.Request(url=response.urljoin(link),
                                 callback=functools.partial(self.parse_condition, condition))
