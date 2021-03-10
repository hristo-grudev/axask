import scrapy
from scrapy.exceptions import CloseSpider

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import AxaskItem
from itemloaders.processors import TakeFirst


base = "https://www.axa.sk/o-nas/pre-media/tlacove-spravy/?news={}"


class AxaskSpider(scrapy.Spider):
	name = 'axask'
	page = 1
	start_urls = [base.format(page)]
	urls_list = []

	def parse(self, response):
		post_links = response.xpath('//article/a/@href').getall()

		for url in post_links:
			if url in self.urls_list:
				raise CloseSpider('no more pages')
			self.urls_list.append(url)
			yield response.follow(url, self.parse_post)

		self.page += 1
		next_page = base.format(self.page)
		yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		title = response.xpath('//div[@class="newsDetail"]/h1/text()').get()
		description = response.xpath('//div[@class="perex"]//text()|//div[@class="htmlText"]//text()[normalize-space() and not(ancestor::ul | ancestor::h3)]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//time/text()').get()

		item = ItemLoader(item=AxaskItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
