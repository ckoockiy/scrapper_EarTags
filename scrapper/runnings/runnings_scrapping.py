from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from time import sleep
from user_agent import generate_user_agent

import pandas as pd
import re

from config import logger
import logging


class RunningsScrapper:

    def __init__(self):
        self.lista_productos = []
        self.driver = None
        self.timeout = 10
        self.start_driver()

    def start_driver(self):
        chrome_options = webdriver.ChromeOptions()

        custom_headers = {
            'Host': 'www.runnings.com',
            "User-Agent": generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }

        for header, value in custom_headers.items():
            chrome_options.add_argument(f"--{header}={value}")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

    def close_popup(self):

        try:
            # Haz clic en el botón de cierre para cerrar la ventana emergente
            close_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ltkpopup-close"))
            )
            close_button.click()
        except TimeoutException:
            # Manejar una excepción si no se puede encontrar el elemento a tiempo
            print("El botón de cierre no se encontró a tiempo.")
        except ElementClickInterceptedException:
            # Manejar una excepción si no se puede hacer clic en el elemento (intercepción de clic)
            print(
                "No se puede hacer clic en el botón de cierre debido a la intercepción de clic.")
        except Exception as e:
            # Manejar otras excepciones inesperadas
            print(f"Se produjo una excepción inesperada: {str(e)}")

    def count_pagination_tiles(self):

        # contar num de paginas:
        pagination_element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "pagination-root-Zi3"))
        )

        # Encuentra todos los elementos con la clase "pagination-tile-mou" dentro del elemento de paginación
        pagination_tiles = pagination_element.find_elements(
            By.CLASS_NAME, "pagination-tile-mou")

        # Cuenta cuántos elementos se encontraron
        count = len(pagination_tiles)

        # Imprime el resultado
        print(f"El elemento 'pagination-tile-mou' aparece {count} veces.")
        return int(count)

    def get_product_urls(self):

        wait = WebDriverWait(self.driver, self.timeout)
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "item-name-5FM")))

        # Itera a través de los elementos y obtén sus atributos "href"
        hrefs = [element.get_attribute("href") for element in elements]

        filtered_urls = [url for url in hrefs if (
            "blank-tag" in url or "ear-tag" in url or "insecticide" in url) and "saddle" not in url]

        return filtered_urls

    def requests_url(self, url):
        self.driver.get(url)

    def get_data_product(self, url):
        self.driver.get(url)
        self.close_popup()

        '''
            # obtenemos el nombre del producto
            nombre_producto = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "productFullDetail-productName-d5V")))

            print(nombre_producto.text)
        '''
        # Espera a que el elemento esté presente
        wait = WebDriverWait(self.driver, self.timeout)
        elemento_div = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.yotpo-main-widget')))

        # Obtén los atributos que deseas del elemento
        data_price = elemento_div.get_attribute('data-price')
        data_name = elemento_div.get_attribute('data-name')
        data_image_url = elemento_div.get_attribute('data-image-url')

        # Imprime los atributos
        # print("data-price:", data_price)
        # print("data-name:", data_name)
        # print("data-image-url:", data_image_url +"?auto=webp&format=pjpg&width=449&height=449&quality=85")

        # descripcion del producto
        meta_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//meta[@name="description"]')))

        data_description = meta_element.get_attribute("content")
        # print("Descripcion: ", data_description)

        # detalles del producto
        div_element = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, 'details-description-YRV')))
        div_text = div_element.text
        # print(div_text)

        data_sin_procesar = [data_price, data_name,
                             data_image_url, data_description, div_text]
        self.lista_productos.append(data_sin_procesar)

    def process_data_to_df(self):
        print("Creando Dataframe...!")
        columns = ["Imagen", "Brand", "Nombre", "1-Piece or 2-Piece", "Animal Compatibility", "Blank or Numbered", "Letter or Number Size", "Quantity", "Color",
                   "Material", "Height", "Length", "Weight", "Width", "Manufacturer", "Part Number", "snap-lock", "longer neck", "UV inhibitors", "Insecticide", "Precio"]

        cantidad_regex = r'(\d+)\s*(?:Pack|/Pkg)'

        animales = ["Calves", "Cattle", "Livestock", "Sheep", "Pigs", "Goats"]

        # df_final = pd.DataFrame(columns=columns)
        data_rows = []

        for producto in self.lista_productos:
            row_data = {}

            imagen = producto[2]
            precio = producto[0]

            row_data["Imagen"] = imagen
            row_data["Precio"] = precio

            # print("Nombre ", producto[1])

            if "Y-Tex" in producto[1]:
                row_data["Brand"] = "Y-Tex"

            if "All-American" in producto[1]:
                row_data["Nombre"] = "All-American"

            if "Z Tags" in producto[1]:
                row_data["Nombre"] = "Z Tags"

            if "Dominator" in producto[1]:
                row_data["Nombre"] = "Dominator"

            # print("Imagen: ",producto[2])
            # print("Descripcion: ", producto[3])
            # print("Detalles: ", producto[4])

            matches = re.findall(cantidad_regex, producto[1])
            if matches:
                cantidad_por_paquete = int(matches[0])
                row_data["Quantity"] = cantidad_por_paquete
                # print(f'Cantidad por paquete para "{nombre_producto}": {cantidad_por_paquete}')

            if "One-Piece" in producto[1] or "1-piece" in producto[3]:
                row_data["1-Piece or 2-Piece"] = "1-Piece Design"

            if "2-Piece" in producto[1] or "2-piece" in producto[3]:
                row_data["1-Piece or 2-Piece"] = "2-Piece Design"

            coincidencias = [
                animal for animal in animales if animal.lower() in str(producto[3]).lower()]

            if coincidencias:
                row_data["Animal Compatibility"] = coincidencias

            if "blank" in producto[1].lower() or "blank" in producto[3].lower():
                row_data["Blank or Numbered"] = "Blank"

            if "numbered" in producto[1].lower() or "numbered" in producto[3].lower():
                row_data["Blank or Numbered"] = "Numbered"

            if "polyurethane" in producto[4].lower() or "polyurethane" in producto[3].lower():
                row_data["Material"] = "Polyurethane"

            if "plastic" in producto[4].lower() or "plastic" in producto[3].lower():
                row_data["Material"] = "Plastic"

            if "Snap-Lok" in producto[4] or "Snap-Lok" in producto[3]:
                row_data["snap-lock"] = "Ok"

            if "longer neck" in producto[4].lower() or "longer neck" in producto[3].lower():
                row_data["longer neck"] = "Ok"

            if "inhibitors" in producto[4].lower() or "inhibitors" in producto[3].lower():
                row_data["UV inhibitors"] = "Ok"

            if "insecticide" in producto[4].lower() or "insecticide" in producto[3].lower() or "insecticide" in producto[1]:
                row_data["Insecticide"] = "Ok"

            data_rows.append(row_data)
        df_final = pd.DataFrame(data_rows, columns=columns)
        print("--------------------------------------------------------")
        # df_final = df_final.append(row_data, ignore_index=True)
        print(df_final)
        print("--------------------------------------------------------")
        return df_final
