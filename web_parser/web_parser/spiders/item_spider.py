import scrapy


class ItemSpider(scrapy.Spider):
    name = "items"

    def start_requests(self):
        urls = [
            'https://smartytitans.com/live/research',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'items-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
