import re
import csv
import scrapy

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    URL = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'

    fieldnames = [
        "item_name", "item_url", "item_price", "item_rating", 
        "item_no_of_reviews", "asin", "description", "manufacturer"
    ]

    # making requests to the URL
    def start_requests(self):
        # open csv file and write headers
        with open("products_1.csv", "w") as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=self.fieldnames)
            writer.writeheader()

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
                "item_url": response.urljoin(item_url),
                "item_price": item_price,
                "item_rating": item_rating,
                "item_no_of_reviews": item_no_of_reviews
            })

        # redirecting to each product's page for scraping more information
        for info in items_info:
            request = scrapy.Request(url=info["item_url"], callback=self.parse_product)
            request.meta["item_info"] = info
            yield request

        # redirecting to next page
        next_page = response.css("a.s-pagination-item.s-pagination-next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


    def parse_product(self, response):
        """Parse additional information from product's page"""

        info = response.meta["item_info"]
        info["description"] = self.get_description(response)
        info["manufacturer"] = self.get_manufacturer(response)

        # ASIN from URL
        asin_pattern = re.compile(r"/dp/([0-9A-Z]{10})")
        asin = re.search(asin_pattern, info["item_url"])
        info["asin"] = asin[1] if asin else None

        # # getting absolute url
        # info["item_url"] = response.urljoin(info["item_url"])

        # formatting item_rating
        if info["item_rating"]:
            info["item_rating"] = info["item_rating"].strip().split()[0]

        # save each entry to csv file
        with open("products_1.csv", "a") as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=self.fieldnames)
            writer.writerow(info)


    def get_manufacturer(self, response):
        """Parses manufacturer name from given product's page."""

        manufacturers = response.xpath(
            "//*[contains(text(), 'Manufacturer')]/following-sibling::*"+
            "[not(self::style or self::link or self::script)]//text()|"+
            "//*[contains(text(), 'Manufacturer')][not(self::style)]/"+
            "ancestor::div[1]/following-sibling::div[1]//text()"
        ).getall()

        if not manufacturers: return None

        # reformatting potential manufacturers
        manufacturers = list(map(self.reformat_string, manufacturers))

        manufacturers = " ".join(manufacturers)
        return self.remove_unwanted_words(manufacturers)


    def get_description(self, response):
        """Parses product's description from given product's page."""

        description = response.xpath(
            "//*[@class='product-facts-title']/following-sibling::*//text()|"+
            "//*[@id='feature-bullets' or @id='productDescription']//text()"
        ).getall()

        # reformatting description
        description = list(map(self.reformat_string, description))
        description = " ".join(description)

        return self.remove_unwanted_words(description)

    def reformat_string(self, string):
        """removes unwanted characters from the passed string"""

        string = re.sub(r'[^\x00-\x7F]|\n|:', "", string).strip().lower()
        string = re.sub(r'\s+', " ", string)
        return string

    def remove_unwanted_words(self, string):
        """removes unwanted words from the string"""

        pattern = re.compile(r"no|yes|see|this|more|items|about|view|info")
        string = re.sub(pattern, "", string)
        string = re.sub(r'\s+', " ", string)
        return string
