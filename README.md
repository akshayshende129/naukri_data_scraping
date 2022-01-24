# Naukri.com Data Scraping using Scrapy

This a web scraper created to scrape the Naukri.com.
Which extract the data based on the skills and with there respective Job Descriptions.

## Installation & Executions
```
1. Create a new folder named as naukri
2. Create Python(3.8+) environment 
3. Clone the repository into the folder
4. Create a data folder under naukri root folder to save data
5. Activate newly created environment
6. Install the required library using 
    pip install -r requirements.txt
7. Running Naurkri Web Scrapper
    a. With Logs
        scrapy runspider naukri.py
    b. Without logs
        scrapy runspider --nolog naukri_jd.py
```

## Further Scope
    1. Adding resume capabilities.
    2. Multithreading for simulataneous data-processing.
    3. Dynamic Keywords
