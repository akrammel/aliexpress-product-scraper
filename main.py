import requests, json, re, wget, os, hashlib, html2text

# Loading config
config = json.loads(open("config.json", "r").read())

# Product url
url = input("Product URL: ")

# Getting product information
product = None
product_i = {}
while product is None:
    product_i["id"] = re.search('https://www.aliexpress.com/item/(.*)\.html', url).group(1)
    # Product directory creation
    try:
        os.mkdir('products/'+product_i["id"])
    except:
        pass

    r = requests.get(url, headers={"User-Agent": config["user-agent"]})
    product = re.search('data: (.*)csrfToken', r.text, flags=re.DOTALL)

    if product is not None:
        product = product.group(1).strip()[:-1]
        product = json.loads(product) 
        product_i["title"] = re.sub("\|   - AliExpress","",product["pageModule"]["title"])
        desc = requests.get(product["descriptionModule"]["descriptionUrl"], headers={"User-Agent": config["user-agent"]}).text
        open("products/"+product_i["id"]+"/"+product_i["id"]+".html", "w+").write(desc)
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        open("products/"+product_i["id"]+"/"+product_i["id"]+".txt", "w+").write(h.handle(desc))
        product_i["localDescription"] = product_i["id"]+".html"
        product_i["localDescriptionText"] = product_i["id"]+".txt"
        product_i["localImages"] = []
        product_i["price"] = {}
        if product["priceModule"]["discountPromotion"]:
            product_i["price"]["discount"] = str(product["priceModule"]["discount"])+"%"
            product_i["price"]["new_price"] = product["priceModule"]["formatedActivityPrice"]
            product_i["price"]["old_price"] = product["priceModule"]["formatedPrice"]
        else:
           product_i["price"]["unchanged_price"] = product["priceModule"]["formatedPrice"] 
        
        # Downloading images
        for i in product["imageModule"]["imagePathList"]:
            path = 'products/'+product_i["id"]+"/"+hashlib.md5(i.encode()).hexdigest()+"."+i.split(".")[-1]
            product_i["localImages"].append(hashlib.md5(i.encode()).hexdigest()+"."+i.split(".")[-1])
            if(not os.path.isfile(path)):
                wget.download(i, path)

        open("products/"+product_i["id"]+"/"+product_i["id"]+".json", "w+").write(json.dumps(product_i, indent=4))