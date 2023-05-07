DRIVER_PATH = '/Users/kartik/Documents/chromedriver_mac64'

import time 
import json
 
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions() 
options.add_argument("--headless")
options.page_load_strategy = 'none' 
chrome_path = ChromeDriverManager().install() 
chrome_service = Service(chrome_path) 
driver = Chrome(options=options, service=chrome_service) 
driver.implicitly_wait(5)

def get_products(url):
        
    driver.get(url) 
    time.sleep(10)

    items = driver.find_elements(By.CSS_SELECTOR, ".item.prod-deck.row.ng-scope")
    products = []

    for item in items:
        try:
            curr_item = {}
            prod_name_element = item.find_element(By.CSS_SELECTOR, "div.prod-name")
            brand_name_text = prod_name_element.find_element(By.TAG_NAME, "h6").text
            sku_name_text = prod_name_element.find_element(By.TAG_NAME, "a").text

            sku_size_element_text = item.find_element(By.CSS_SELECTOR, "div.qnty-selection").find_element(By.CSS_SELECTOR, "span.ng-scope").find_elements(By.TAG_NAME, "span")[0].text
            mrp = item.find_element(By.CSS_SELECTOR, "span.mp-price").text
            sp = item.find_element(By.CSS_SELECTOR, "span.discnt-price").text 

            out_of_stock = False
            try:
                qty_input = item.find_element(By.CSS_SELECTOR, "div.input-group")
            except:
                out_of_stock = True
            
            image = item.find_element(By.TAG_NAME, "img")
            img_src = image.get_attribute("src")

            a_tag = item.find_element(By.TAG_NAME, "a")
            link = a_tag.get_attribute("href")
            sku_id = link.split("/")[4]


            curr_item["brand_name"] = brand_name_text
            curr_item["sku_name"] = sku_name_text
            curr_item["sku_size"] = sku_size_element_text
            curr_item["mrp"] = mrp
            curr_item["sp"] = sp
            curr_item["Image"] = img_src
            curr_item["Link"] = link
            curr_item["SKU_ID"] = sku_id
            
            if out_of_stock:
                curr_item["Out of Stock?"]="Yes"
            else:
                curr_item["Out of Stock?"]="No"

            products.append(curr_item)
            # print(curr_item)
        except:
            pass

    return products
    
def get_p1_categories(url):
    driver.get(url) 
    time.sleep(10)

    subcategories = driver.find_elements(By.CSS_SELECTOR, ".col-xs-12.checkbox.subcat.ng-scope")
    subcategory_dict = {}

    for category in subcategories:
        
        a_tag = category.find_element(By.TAG_NAME, "a")
        href = a_tag.get_attribute('href')
        text = category.find_element(By.CSS_SELECTOR, "div.ng-scope").text

        if text == "":
            continue
        subcategory_dict[text] = href

    return subcategory_dict



def get_p2_categories(url):
    driver.get(url) 
    time.sleep(10)

    p2_categories = driver.find_elements(By.CSS_SELECTOR, ".col-xs-12.checkbox.subcat2.ng-scope")
    p2_category_dict = {}

    for category in p2_categories:
        
        a_tag = category.find_element(By.TAG_NAME, "a")
        href = a_tag.get_attribute('href')
        text = category.find_element(By.CSS_SELECTOR, "div.ng-scope").text

        if text == "":
            continue
        p2_category_dict[text] = href

    return p2_category_dict


p0_categories = {
    'Fruits & Vegetables': 'https://www.bigbasket.com/cl/fruits-vegetables/?nc=nb',
    'Foodgrains, Oil & Masala': 'https://www.bigbasket.com/cl/foodgrains-oil-masala/?nc=nb',
    'Bakery, Cakes & Dairy': 'https://www.bigbasket.com/cl/bakery-cakes-dairy/?nc=nb',
    'Beverages': 'https://www.bigbasket.com/cl/beverages/?nc=nb',
    'Snacks & Branded Foods': 'https://www.bigbasket.com/cl/snacks-branded-foods/?nc=nb'
}

products = []

my_data = {}

for super_category in p0_categories:
    try:   
        super_category_link = p0_categories[super_category]

        p1_categories = get_p1_categories(super_category_link)

        print("Fetching for super category "+super_category)
        my_data[super_category] = {}
        
        for category in p1_categories:
            category_link = p1_categories[category]

            print("Fetching for category "+category)
            my_data[super_category][category] = {}
            p2_categories = get_p2_categories(category_link)
            
            for sub_category in p2_categories:
                sub_category_link = p2_categories[sub_category]

                print("Fetching for subcategory "+sub_category)
                my_data[super_category][category][sub_category] = sub_category_link
                
    except:
        pass
    

ans_data = []
for super_category in my_data:
    for category in my_data[super_category]:
        for sub_category in my_data[super_category][category]:
            sub_category_link = my_data[super_category][category][sub_category]
            print(f"\n\n fetching products for {super_category} -> {category} -> {sub_category} \n\n")
            products = get_products(sub_category_link)
            ans = {}
            for product in products:
                ans["Super Category P0"] = super_category
                ans["Category P1"] = category
                ans["Sub Category P2"] = sub_category
                ans["SKU ID"] = product["SKU_ID"]
                ans["Image"] = product["Image"]
                ans["Brand"] = product["brand_name"]
                ans["SKU NAME"] = product["sku_name"]
                ans["SKU SIZE"] = product["sku_size"]
                ans["MRP"] = product["mrp"]
                ans["SP"] = product["sp"]
                ans["LINK"] = product["Link"]
                ans["Out of Stock?"] = product["Out of Stock?"]
                
                ans_data.append(ans)  
                    
driver.quit()

with open('output.txt', 'w') as convert_file:
     convert_file.write(json.dumps(ans_data, indent=2))
     