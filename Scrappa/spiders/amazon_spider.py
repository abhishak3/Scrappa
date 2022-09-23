import scrapy
import re
import csv

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    URL = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

    # making requests to the URL
    def start_requests(self):
        yield scrapy.Request(url=self.URL, callback=self.parse)


    def parse(self, response):
        """Parses each response after request is processed."""

        items_info = []
        items = response.css("div.s-result-item.s-widget-spacing-small")

        # getting required fields from each item
        for item in items:
            item_name = item.css("span.a-size-medium.a-color-base::text").get()
            item_url = item.css("h2 a.a-link-normal::attr(href)").get()
            item_price = item.css("span.a-price-whole::text").get()
            item_rating = item.css("div.a-row.a-size-small span.a-icon-alt::text").get()
            item_no_of_reviews = item.css("span.a-size-base.s-underline-text::text").get()

            items_info.append({
                "item_name": item_name,
                "item_url": item_url,
                "item_price": item_price,
                "item_rating": item_rating,
                "item_no_of_reviews": item_no_of_reviews
            })

        # redirecting to each product's page for scraping more information
        for info in items_info:
            request = response.follow(info["item_url"], callback=self.parse_product)
            request.meta["item_info"] = info
            yield request

        # redirecting to next page
        next_page = response.css("a.s-pagination-item.s-pagination-next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


    def parse_product(self, response):
        """Parse additional information from product's page"""

        info = response.meta["item_info"]
        asin = re.findall(r"[0-9A-Z]{10}", info["item_url"]) # regex for ASIN number
        info["asin"] = asin[-1] if asin else None
        info["description"] = self.get_description(response)
        info["manufacturer"] = self.get_manufacturer(response)

        # fieldnames for csv file
        fieldnames = [
            "item_name", "item_url", "item_price", "item_rating", 
            "item_no_of_reviews", "description", "manufacturer", "asin"
        ]

        # save each entry to csv file
        with open("products_1.csv", "a") as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
            writer.writerow(info)


    def get_manufacturer(self, response):
        """Parses manufacturer name from given product's page."""

        # getting and reformatting potential manufacturers
        manufacturers = response.xpath("//*[contains(text(), 'Manufacturer')]/following-sibling::*/text()").getall()
        manufacturers = list(map(lambda string : re.sub(r"\u200f|\u200e|\n|\s|:", "", string).lower(), manufacturers))

        if not manufacturers: return None

        for manufacturer in manufacturers:
            if manufacturer not in ("no", "yes"):
                return manufacturer
        

    def get_description(self, response):
        """Parses product's description from given product's page."""

        description = response.xpath(
            "//*[@class='product-facts-title']/following-sibling::*//text()|"+
            "//*[@id='feature-bullets' or @id='productDescription']//text()"
        ).getall()
        return " ".join(description)