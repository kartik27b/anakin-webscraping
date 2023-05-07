import requests
import json
from seleniumwire import webdriver
import time
import json
from seleniumwire.utils import decode as sw_decode


def get_data(captcha_token):
    url = "https://portal.grab.com/foodweb/v2/search"

    payload = {
        "latlng": "14.5238590003,120.992159",
        "keyword": "",
        "offset": 0,
        "pageSize": 32,
        "countryCode": "PH"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json;charset=utf-8',
        'Referer': 'https://food.grab.com/',
        'X-GFC-Country': 'PH',
        'X-Grab-Web-App-Version': '7JxnV__dTfJZAKF80UUJO',
        'X-Country-Code': 'PH',
        'X-Recaptcha-Token': captcha_token,
        'Origin': 'https://food.grab.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Connection': 'keep-alive',
        'TE': 'trailers'
    }

    count = 1

    final_data = []
    while True:
        print(f"\n\n performing request {count} ", end="\n\n")
        count = count + 1
        json_payload = json.dumps(payload)
        response = requests.request("POST", url, headers=headers, data=json_payload)
        data = json.loads(response.text)["searchResult"]
        hasMore = data.get("hasMore", False)
        restaurants = data["searchMerchants"]

        for restaurant in restaurants:
            name = restaurant["address"]["name"]
            latlng = restaurant["latlng"]
            latitude = latlng["latitude"]
            longitude = latlng["longitude"]

            curr_data = {}
            curr_data['name'] = name
            curr_data['latlng'] = latlng
            
            final_data.append(curr_data)

        if hasMore:
            payload['offset'] += 32
            continue
        else:
            break


    print(json.dumps(final_data, indent=2))
    with open('grab_data3.txt', 'w') as convert_file:
        convert_file.write(json.dumps(final_data, indent=2))





options = {}

driver = webdriver.Chrome(seleniumwire_options=options)

driver.get('https://food.grab.com/ph/en/restaurants')
driver.implicitly_wait(5)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(40)


for request in driver.requests:
    if request.response:
        if request.url.startswith("https://www.google.com/recaptcha/api2/reload"):
            data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            data = data.decode("utf8")
            data2 = json.loads(data[4:])
            captcha_token = data2[1]
            
            print(f"captcha token {captcha_token}")
            get_data(captcha_token)
            break

