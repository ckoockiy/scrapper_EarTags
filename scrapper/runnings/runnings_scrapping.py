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
        """
            Inicia un controlador de Selenium con opciones personalizadas y maximiza la ventana del navegador.

            Raises:
                WebDriverException: Si ocurre un error al iniciar el controlador de Selenium.

            Note:
                Esta función utiliza opciones personalizadas para configurar el controlador de Selenium
                y establece las preferencias del navegador antes de maximizar la ventana del navegador.
        """
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

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
        except WebDriverException as e:
            logging.error(f"Error al iniciar el controlador de Selenium: {e}")

    def close_popup(self):
        """
            Cierra una ventana emergente en la página web.

            Intenta hacer clic en el botón de cierre de la ventana emergente. Si el botón no se encuentra a tiempo
            o no se puede hacer clic debido a la intercepción de clic, se manejan las excepciones apropiadas y se
            registran mensajes informativos. Si ocurre una excepción inesperada, se registra un mensaje de error.

            Args:
                self (objeto): La instancia del objeto que llama a esta función.

            Returns:
                None
        """

        try:
            # Haz clic en el botón de cierre para cerrar la ventana emergente
            close_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ltkpopup-close"))
            )
            close_button.click()
        except TimeoutException:
            # Manejar una excepción si no se puede encontrar el elemento a tiempo
            logging.info("El botón de cierre no se encontró a tiempo.")
        except ElementClickInterceptedException:
            # Manejar una excepción si no se puede hacer clic en el elemento (intercepción de clic)
            logging.info(
                "No se puede hacer clic en el botón de cierre debido a la intercepción de clic.")
        except Exception as e:
            # Manejar otras excepciones inesperadas
            logging.error(f"Se produjo una excepción inesperada: {str(e)}")

    def count_pagination_tiles(self):
        """
        Cuenta el número de elementos de paginación en una página web.

        Returns:
            int: El número de elementos de paginación encontrados.
        """
        try:
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

            return int(count)
        except TimeoutException:
            logging.error(
                "Se agotó el tiempo de espera al contar las páginas.")
            return 0
        except Exception as e:
            logging.error(f"Se produjo una excepción inesperada: {str(e)}")
            return 0

    def get_product_urls(self):
        """
            Obtiene las URLs de productos que cumplen con ciertos criterios de filtro.

            Returns:
                list: Una lista de URLs de productos filtrados.
        """
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            elements = wait.until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "item-name-5FM")))

            # Itera a través de los elementos y obtén sus atributos "href"
            hrefs = [element.get_attribute("href") for element in elements]

            filtered_urls = [url for url in hrefs if (
                "blank-tag" in url or "ear-tag" in url or "insecticide" in url) and "saddle" not in url]

            return filtered_urls
        except TimeoutException:

            logging.error(
                "Se agotó el tiempo de espera al obtener las URLs de los productos.")
            return []
        except Exception as e:

            logging.error(f"Se produjo una excepción inesperada: {str(e)}")
            return []

    def requests_url(self, url):
        """
            Realiza una solicitud GET a la URL especificada.

            Args:
                url (str): La URL a la que se realizará la solicitud.

            Returns:
                None
        """
        try:
            self.driver.get(url)
        except TimeoutException:

            logging.error(
                f"No se pudo cargar la URL: {url}. Se agotó el tiempo de espera.")
        except Exception as e:

            logging.error(
                f"Se produjo una excepción inesperada al cargar la URL: {str(e)}")

    def get_data_product(self, url):
        """
            Obtiene datos del producto a partir de una URL dada.

            Args:
                url (str): La URL del producto.

            Returns:
                None
        """
        try:
            self.driver.get(url)
            self.close_popup()

            # Espera a que el elemento esté presente
            wait = WebDriverWait(self.driver, self.timeout)
            elemento_div = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.yotpo-main-widget')))

            # Obtén los atributos que deseas del elemento
            data_price = elemento_div.get_attribute('data-price')
            data_name = elemento_div.get_attribute('data-name')
            data_image_url = elemento_div.get_attribute('data-image-url')

            # descripcion del producto
            meta_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//meta[@name="description"]')))

            data_description = meta_element.get_attribute("content")
            # print("Descripcion: ", data_description)

            # detalles del producto
            div_element = wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'details-description-YRV')))
            div_text = div_element.text

            data_sin_procesar = [data_price, data_name,
                                 data_image_url, data_description, div_text]
            self.lista_productos.append(data_sin_procesar)
        except Exception as e:
            logging.error(f"Se produjo una excepción inesperada: {str(e)}")

    def process_data_to_df(self, filename_excel):
        """
            Procesa los datos recopilados y los guarda en un archivo Excel.

            Args:
                filename_excel (str): Nombre del archivo Excel en el que se guardarán los datos.

            Returns:
                None
        """
        try:
            columns = ["Imagen", "Brand", "Nombre", "1-Piece or 2-Piece", "Animal Compatibility", "Blank or Numbered", "Letter or Number Size", "Quantity", "Color",
                       "Material", "Height", "Length", "Weight", "Width", "Manufacturer", "Part Number", "snap-lock", "longer neck", "UV inhibitors", "Insecticide", "Precio"]

            cantidad_regex = r'(\d+)\s*(?:Pack|/Pkg)'

            animales = ["Calves", "Cattle",
                        "Livestock", "Sheep", "Pigs", "Goats"]

            data_rows = []

            for producto in self.lista_productos:
                row_data = {}

                imagen = producto[2]
                precio = producto[0]

                row_data["Imagen"] = imagen
                row_data["Precio"] = precio

                if "Y-Tex" in producto[1]:
                    row_data["Brand"] = "Y-Tex"

                if "All-American" in producto[1]:
                    row_data["Nombre"] = "All-American"

                if "Z Tags" in producto[1]:
                    row_data["Nombre"] = "Z Tags"

                if "Dominator" in producto[1]:
                    row_data["Nombre"] = "Dominator"

                matches = re.findall(cantidad_regex, producto[1])
                if matches:
                    cantidad_por_paquete = int(matches[0])
                    row_data["Quantity"] = cantidad_por_paquete

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

            df_final.to_excel(filename_excel, index=False)
        except Exception as e:
            logging.error(f"Se produjo una excepción inesperada: {str(e)}")
