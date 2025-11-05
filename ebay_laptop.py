from http.client import responses

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import random
import time

def random_delay(min_seconds = 3, max_seconds = 8):
    #Im doing this to try and to make it more human
    delay = random.uniform(min_seconds, max_seconds)
    print(f"Waiting {delay:.1f} seconds ")
    time.sleep(delay)

def obtener_html():
    #gets the HTML
    url =  "https://www.ebay.com/sch/i.html?_nkw=gaming+laptop&_sacat=0&_udlo=500&_udhi=2000"
    headers = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.ebay.com/',
        'DNT': '1',  # Do Not Track - señal de privacidad
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
     }
    try:
        print(f"Doing a request to url {url}")
        random_delay()
        response = requests.get(url, headers = headers, timeout = 10)
        random_delay()
        if response.status_code == 200:
            print("Conection succesfully")
            return response.content
        else:
            print(f"Error code {response.status_code}")
            return None


    except Exception as e:
        print("Error")
        return None



def extraer_listings(html):
    #Gets the listing from ebay
    random_delay()
    soup = BeautifulSoup(html, 'html.parser')

    listing = soup.find_all('div', class_ = 'su-card-container__content')

    print(f"We found {len(listing)} total listings")
    return listing

def examinar_primer_listing(listing):
        # Examines the structure of the first listing to understand data
        if listing:
            # Saltar los primeros 2-3 listings que son anuncios
            primer_listing_real = listing[3]

            # extracts the title
            titulo_element = primer_listing_real.find('span', class_='su-styled-text primary default')
            titulo = titulo_element.text.strip() if titulo_element else "Not found"
            print(f"Title: {titulo}")

            # extract price
            precio_container = primer_listing_real.find('div', class_='su-card-container__attributes__primary')
            if precio_container:
                precio_element = precio_container.find('span', class_='s-card__price')
                precio = precio_element.text.strip() if precio_element else "Not found"
            else:
                precio = "Not found"

            print(f"Price: {precio}")

            # Extract URL
            url_element = primer_listing_real.find('a', class_='su-link')
            url = url_element.get('href') if url_element else "Not found"
            print(f"URL: {url}")

            # debug
            print("HTML of the REAL listing")
            print(primer_listing_real.prettify()[:1500])

def extraer_datos_listings(listing):
    #Extracts the title, price and url of an individual listing
    try:
        #Extracts the title
        titulo_element = listing.find('span', class_='su-styled-text primary default')

        titulo = titulo_element.text.strip() if titulo_element else "Not found"

        #extract price

        precio_container =  listing.find('div', class_='su-card-container__attributes__primary')
        precio = 'Not found'
        if precio_container:
            precio_element = precio_container.find('span', class_='s-card__price')
            precio = precio_element.text.strip() if precio_element else "Not found"

        #Extract URL
        url_element = listing.find('a', class_='su-link')
        url = url_element.get('href') if url_element else "Not found"

        return {
            'titulo': titulo,
            'precio': precio,
            'url': url
        }

    except Exception as e:
        print(f"There was a mistake extracting data {e}")
        return None

def procesar_todos_listing(listing):
    #Processes all the listings and creates a dictionary

    datos_listings = []

    print("Processing data")

    for i, listing in enumerate(listing):

        if i < 3:
            continue

        random_delay(2, 5)
        datos = extraer_datos_listings(listing)
        if datos:
            datos_listings.append(datos)
            print(f'Listing {i+1}: {datos['titulo'][:50]}...')

    print(f"listing processed {len(datos_listings)}")
    return datos_listings

def guardar_csv(datos, ebay_laptops):
    #Saves data in a CSV file

    try:
        df = pd.DataFrame(datos)

        os.makedirs('datos', exist_ok= True)

        df.to_csv(ebay_laptops, index= False, encoding= 'utf-8')
        print(f"Data saved the name is : {ebay_laptops}")
        print(f"columms: {', '.join(df.columns)}")
        print(f"Saved rows: {len(df)}")

        return True
    except Exception as e:
        print(f"There was a mistake making the CSV: {e}")
        return False

def main():
    print("Starting Ebay scraper")
    html = obtener_html()
    if html:
        listing = extraer_listings(html)
        if listing:
            print(f"We have {len(listing)} total listings")

            datos_listings = procesar_todos_listing(listing)

            if datos_listings:

                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                ebay_laptops = f"datos/raw_{fecha_actual}.csv"

                guardar_csv(datos_listings, ebay_laptops)

                print('Scraping done succesfully')
                print(f'File {ebay_laptops}')
                print(f'Saved listings {len(datos_listings)}')

            else:
                print('We couldnt extract anything')
        else:
            print("No se encontraron listings")
    else:
        print("We couldnt get the html")

main()