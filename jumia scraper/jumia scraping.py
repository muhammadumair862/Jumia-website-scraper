#   &&&&&&&&&& Import Libraries &&&&&&&&
import requests as req
import bs4
import sys
import os
import time
import random
import xml.etree.ElementTree as ET
import lxml.etree

url_web=''
img_url,price,title,brand,category,page_url,description=[],[],[],[],[],[],[]


# &&&&&&&&  Function to Extract Page  &&&&&&&&&
def extract_page(url):
    global url_web
    if 'jumia.com.ng/' in url:
        url_web='https://www.jumia.com.ng'
    elif 'jumia.co.ke/' in url:
        url_web='https://www.jumia.co.ke'
    elif 'jumia.com.gh/' in url:
        url_web='https://www.jumia.com.gh'
    else:
        print("!!! This URL not related to jumia website ")
        sys.exit()

    resp=req.get(url)
    page = bs4.BeautifulSoup(resp.content, "lxml")
    return page


#  &&&&&&&& Function to Preprocess/Extract information  &&&&&&&&
def preprocess_data(page):
    global url_web
    products = page.find_all('div', attrs={'class': '-paxs row _no-g _4cl-3cm-shs'})
    if len(products) > 0:
        k = 1
        try:
            for product in products[0].find_all('article'):
                product_page = extract_page(
                    url_web + product.a['href'])  # crawle products url page & fetch description

                des = product_page.find('div', attrs={'class': 'markup -mhm -pvl -oxa -sc'})

                print(k, "Product Page Url: ", url_web + product.a['href'])
                print('  Product Image Url: ', product.img['data-src'])
                print('  Product Category: ', product.a['data-category'])
                print('  Product Name: ', product.a['data-name'])
                print('  Product Brand: ', product.a['data-brand'])
                if url_web == 'https://www.jumia.com.ng':
                    print('  Product Price: ',
                          int(product.find('div', attrs={'class': 'prc'}).text[2:].strip().replace(',', '')))
                    price.append(int(product.find('div', attrs={'class': 'prc'}).text[2:].strip().replace(',', '')))
                else:
                    print('  Product Price: ',
                          int(product.find('div', attrs={'class': 'prc'}).text[3:].strip().replace(',', '')))
                    price.append(int(product.find('div', attrs={'class': 'prc'}).text[3:].strip().replace(',', '')))

                print('  Product Description: ', des.text)
                print('' * 2), print("\t\t*********************************************\n")
                k += 1
                page_url.append(url_web + product.a['href'])  # image url
                img_url.append(product.img['data-src'])
                category.append(product.a['data-category'])
                title.append(product.a['data-name'])
                brand.append(product.a['data-brand'])
                description.append(des.text)

                time.sleep(random.randint(5, 15))
        except:
            pass
    else:
        return -1

#  &&&&&&&&&&  Pagination Function  &&&&&&&&&&&
def Scrape_web(url,loop_iter=-1):
    if loop_iter==-1:    # if paginatiion by-default
        p=1
        while True:
            page=extract_page(url+'?page='+str(p)+'#catalog-listing')
            status=preprocess_data(page)
            if status==-1:
                break
            p+=1
    else:
        for i in range(1,loop_iter+1):
            page=extract_page(url+'?page='+str(i)+'#catalog-listing')
            status=preprocess_data(page)
            if status==-1:
                break


#  &&&&&&&&&  Create XML file  &&&&&&&&&
def create_xml(filepath):
    # we make root element
    root = ET.Element("products")

    # insert list element into sub elements
    for user in range(len(price)):
        product = ET.SubElement(root, "product")

        c1 = ET.SubElement(product, "storefront_category")
        c1.text = str(category[user])
        b = ET.SubElement(product, "storefront_brand_name")
        b.text = str(brand[user])
        n1 = ET.SubElement(product, "product_name")
        n1.text = str(title[user])
        p_url = ET.SubElement(product, "product_url")
        p_url.text = str(page_url[user])
        i_url = ET.SubElement(product, "image_url")
        i_url.text = str(img_url[user])
        p1 = ET.SubElement(product, "price")
        p1.text = str(price[user])
        des1 = ET.SubElement(product, "product_description")
        des1.text = str(description[user])

    tree = ET.ElementTree(root)

    # write the tree into an XML file
    tree.write(filepath + "\Output.xml", encoding='utf-8', xml_declaration=True)


# &&&&&&  Run Code  &&&&&&&
if __name__=='__main__':
    url=input("Enter Website URL :")
    file_path=input("Enter path to save scraping file :")
    msg=input("Do you want set no of pages? (press y for yes & n for no) :")
    if msg=='n':
        Scrape_web(url)
        create_xml(file_path)
    elif msg=='y':
        n_page=input("Enter No of Pages :")
        Scrape_web(url,int(n_page))
        create_xml(file_path)
    else:
        print("Invalied Value!!!!")

    print(url_web)