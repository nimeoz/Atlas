import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath('Utils.py'))))
from Utils import write_into_json
import selenium as se
import urllib.request
from selenium import webdriver
import pandas as pd
from tqdm import tqdm
import os
import argparse
from selenium.common.exceptions import NoSuchElementException

class MyBatua:
    def __init__(self):
        self.input_csv_file = '/home/et/Desktop/zvsn/new_data/newcrawlers.csv'  # csv file containing the taxonomy and website source URL's
        self.source_urls_col = 'mybatua'  # Column name having the source URL's in CSV file
        self.taxonomy_col = 'Taxonomy'  # Column name having the taxonomy of the product
        self.map_file = pd.read_csv(self.input_csv_file)
        options = se.webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = se.webdriver.Chrome(chrome_options=options)


    def start_requests(self):
        start_request_list = []
        taxonomy_list = []
        for index, row in self.map_file.dropna(subset=[self.source_urls_col]).iterrows():
            taxonomy = row[self.taxonomy_col]
            source_url = row[self.source_urls_col]
            start_request_list.append(source_url)
            taxonomy_list.append(taxonomy)

        self.parse_items(start_request_list, taxonomy_list)

    def parse_items(self,source_url_list, taxonomy_list):
        try:

            urls = []
            # Each Category URL
            for url,tax in zip(source_url_list,taxonomy_list):
                self.driver.get(url)

                print("Gathering all_items_in_url")
                p_element = self.driver.find_elements_by_css_selector("div.category-products li.item.last a.product-image")
                for e in p_element:
                    print("Getting product URLS")
                    # Gets product urls
                    urls.append(e.get_attribute("href"))

                urls = list(set(urls))
                f = len(urls)
                for each in tqdm(urls):
                    print("Processing URL:"+each)
                    self.driver.implicitly_wait(5)
                    self.parse_product(each,tax)
        except Exception as e:
            # print("Unable to retreive product details"+p_element)
            print("Error in parse_items due to"+str(e))

    def parse_product(self,each_url,taxonomy):
        try:

            product_details = {}
            self.driver.get(each_url)

            web_image_url = self.driver.find_elements_by_css_selector(".product-essential div.product-image-gallery img#image-0")[0]
            web_image_url = web_image_url.get_attribute("src")
            product_details['product_image_url'] = web_image_url

            temp_taxonomy = taxonomy.replace(" ", "_")
            file_path = 'atlas_dataset/' + temp_taxonomy.replace("->",
                                                                 "-") + "/images/"

            # file_path = taxonomy.replace("->","/") + "/" + self.source_urls_col + "/images/"
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            image_name = file_path + web_image_url.split('/')[-1]
            product_details['file_path'] = image_name
            # urllib.request.urlretrieve(web_image_url, image_name)

            product_details['product_page_url'] = each_url
            product_details['product_price'] = self.driver.find_elements_by_css_selector(".price-info div.price-box p.special-price span.price")[0].text
            product_details['product_title'] = self.driver.find_elements_by_css_selector(".product-shop div.product-name span.h1")[0].text
            product_details['taxonomy'] = taxonomy
            product_details['source'] = 'My Batua'
            temp_product_info = self.driver.find_elements_by_css_selector(".std ul li")

            temp = []
            for info in temp_product_info:
                temp.append(info.text)

            product_details['product_info'] = '.'.join(temp)
            json_path = 'atlas_dataset/'+taxonomy.replace("->","-") + "/"
            write_into_json(json_path, product_details)
            print("Wtitten into json",json_path)

        except Exception as e:
            print("Unable to crawl for "+each_url)
            print("Reason: "+str(e))

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Script which splits the data into Train, Validate and Test to train the product_categorization model')
    # parser.add_argument('--destination_path', '-dp', help='Path to atlas_dataset.json destination file')
    # args = parser.parse_args()
    #
    # dest_folder = args.destination_path

    mb = MyBatua()
    mb.start_requests()
