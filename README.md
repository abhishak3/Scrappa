# Scrappa
The Web Crawler to scrape out data of all products from multiple pages (atleast 20) from the following link:

[Required Link](https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1)
```
https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1
```

Scrapped out data is stored in file named `products_1.csv`.


## Installation and Running
### Without virutal environment
1. Install all dependencies from `requirements.txt` file or from the `Pipenv`.
```
pip insatll -r requirements.txt
```
2. Run the following command
```
scrapy crawl amazon
```

### With `pipenv`
1. Make sure `pipenv` is installed
```
pip install pipenv
```
2. Activate pipenv shell
```
pipenv shell
```
or
```
python -m pipenv shell
```
3. Run the web crawler
```
pipenv install && scrapy crawl amazon
```
or
```
python -m pipenv install && scrapy crawl amazon
```

### With `virtualenv`
1. Make sure virtualenv is installed
```
pip install virtualenv
```
2. Create and activate the virtual environment

(Linux or MacOS)
```
python -m venv venv && source venv/bin/activate
```
(windows)
```
python -m venv venv && venv\Scripts\activate
```

3. Install requirements
```
pip install -r requirements.txt
```

4. Activate the crawler
```
scrapy crawl amazon
```
