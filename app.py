"""
TO do list

    -Paginacion
    -Arreglar filtros
    -Marcas
    -Borrar lo de java script




"""








from flask import Flask
import requests
import random
import json
from bs4 import BeautifulSoup
from flask import render_template,request,redirect,url_for
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from pyVinted import Vinted

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

APP_ID = 'GonzaloB-vetement-PRD-c13fa3adc-92179924'
vintedURL = "https://www.vinted.es/catalog?search_text="

vinted = Vinted()
vinted.items.search
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def mezclar_lista(lista_original):
    # Crear una copia, ya que no deberíamos modificar la original
    # https://parzibyte.me/blog/2020/05/31/python-clonar-lista-eliminar-referencia/
    lista = lista_original[:]
    # Ciclo for desde 0 hasta la longitud de la lista -1
    longitud_lista = len(lista)
    for i in range(longitud_lista):
        # Obtener un índice aleatorio
        # https://parzibyte.me/blog/2019/04/04/generar-numero-aleatorio-rango-python/
        indice_aleatorio = random.randint(0, longitud_lista - 1)
        # Intercambiar
        temporal = lista[i]
        lista[i] = lista[indice_aleatorio]
        lista[indice_aleatorio] = temporal
    # Regresarla
    return lista

@app.route('/procesar_buscador', methods=['POST', 'GET'])
def procesar_buscador():
    query = request.form['query']
    condition = request.form['condition']
    category = request.form['category']
    page = int(request.args.get('page', 1))  # Obtener el valor del parámetro 'page' de la solicitud GET
    results_per_page = 60  # Cantidad de resultados por página
    
    api = Finding(appid=APP_ID, config_file=None)
    buscarUrl = vintedURL + query

    api_request = {
        'keywords': query,
        'outputSelector': 'SellerInfo',
        'itemFilter': [
            {'name': 'Condition', 'value': condition},
            {'name': 'ListingType', 'value': 'FixedPrice'},
        ],
        'paginationInput': {
            'pageNumber': page,
            'entriesPerPage': results_per_page
        }
    }

    if category == 'moda-hombre':
        category_filter = {'name': 'Category', 'value': 260012}
    elif category == 'moda-mujer':
        category_filter = {'name': 'Category', 'value': 260010}
    else:
        category_filter = 11450

    if category_filter:
        api_request['itemFilter'].append(category_filter)
    
    response = api.execute('findItemsByKeywords', api_request)

    if hasattr(response.reply, 'searchResult') and hasattr(response.reply.searchResult, 'item'):
        items = response.reply.searchResult.item
    else:
        items = []

    if hasattr(response.reply, 'paginationOutput') and hasattr(response.reply.paginationOutput, 'totalPages'):
        total_pages = response.reply.paginationOutput.totalPages
    else:
        total_pages = 1
    
    #######################################################################################
    
    # Parte de vinted #

    if category == 'moda-hombre':
            buscarUrl += '&catalog[]=5'
    elif category == 'moda-mujer':
            buscarUrl += '&catalog[]=1904'

    if condition == 'New':
        buscarUrl += '&status_ids[]=6'
    elif condition == 'NewOther' or condition == 'ManufacturerRefurbished':
        buscarUrl += '&status_ids[]=1'
    elif condition == 'VeryGood':
        buscarUrl += '&status_ids[]=2'
    elif condition == 'Good':
        buscarUrl += '&status_ids[]=3'
    elif condition == 'Acceptable' or condition == 'Used':
        buscarUrl += '&status_ids[]=4'
    #######################################################################################

    buscarUrl += '?catalog[]=2050&status_ids[]=4' 

    objetos = vinted.items.search(buscarUrl,20,1)
 

  
    #####################################################
    """
    product_data = {
        "name": "Sudadera",
        "image": "https://images.vestiairecollective.com/cdn-cgi/image/q=80,f=auto,/produit/33780570-1_2.jpg",
        "brand": {
            "@type": "Brand",
            "name": "Stussy"
        },
        "offers": {
            "@type": "Offer",
            "url": "https://es.vestiairecollective.com/hombre-ropa/jchalecos/stussy/jerseis-stussy-de-algodon-negro-33780570.shtml",
            "priceCurrency": "EUR",
            "price": "116.00",
            "availability": "OutOfStock",
            "itemCondition": "UsedCondition"
        }
    }
    """
            # Configurar opciones de Chrome para ejecución en segundo plano
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar Chrome en segundo plano sin abrir una ventana

        # Configurar el servicio de ChromeDriver
    selenium_service = Service('/chromedriver_linux64(1)/chromedriver')  # Reemplazar con la ruta a tu chromedriver

        # Crear una instancia del controlador de Chrome
    driver = webdriver.Chrome(service=selenium_service, options=chrome_options)

        # Cargar la página de Grailed
    url = 'https://es.vestiairecollective.com/search/?q=' + query
    driver.get(url) 
    wait = WebDriverWait(driver, 20)
    scripts = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//script[@type="application/ld+json"]')))

    # Lista para almacenar todos los product_data
    product_data_list = []

    # Iterar sobre los scripts y procesar su contenido
    for script in scripts:
        # Obtener el contenido del script
        script_content = script.get_attribute("innerHTML")

        # Analizar el contenido JSON del script
        product_data = json.loads(script_content)
        
        new_product_data = {}
        for key, value in product_data.items():
            new_key = key + "Grailed"
            new_product_data[new_key] = value

        product_data_list.append(new_product_data)

    # Cerrar el controlador de Selenium
    driver.quit()

    # Acceder a los datos de product_data en la lista
    vintedYebay = objetos + items + product_data_list
    objetos_final = mezclar_lista(vintedYebay)

    # Cerrar el driver de Selenium
    driver.quit()


    return render_template('resultados.html', items=items, page=page, total_pages=total_pages, objetos_final = objetos_final)


if __name__ == '__main__':
    app.run()
