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


class RuralkingScrapper:

    def __init__(self):
        # self.url = "https://www.ruralking.com/catalogsearch/result/?&q=ear%20tags&rows=36&view=grid&start=0"
        self.url = "https://www.ruralking.com/search?searchTerm=ear%2520tag"
        self.lista_productos = []
        self.driver = None
        self.timeout = 10

    def start_driver(self):
        chrome_options = webdriver.ChromeOptions()
        custom_headers = {
            "User-Agent": generate_user_agent(),
        }
        for header, value in custom_headers.items():
            chrome_options.add_argument(f"--{header}={value}")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

    def obtener_datos_ruralking(self):

        self.start_driver()
        self.driver.get(self.url)

        photo_elements = WebDriverWait(self.driver, self.timeout).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".MuiCard-root a")))

        # Itera a través de los elementos encontrados
        for photo_element in photo_elements:
            try:
                # Encuentra el elemento img dentro del elemento "photo_element"
                img_element = photo_element.find_element(By.TAG_NAME, "img")

                # Obtiene los atributos href, src y alt
                href = photo_element.get_attribute("href")
                src_img = img_element.get_attribute("src")
                titulo_prod = img_element.get_attribute("alt")

                productos = [href, src_img, titulo_prod]
                self.lista_productos.append(productos)
            except:
                pass

    def process_data_to_df(self, filename_excel):

        columns = ["Imagen", "Brand", "Nombre", "1-Piece or 2-Piece", "Animal Compatibility", "Blank or Numbered", "Letter or Number Size", "Quantity", "Color",
                   "Material", "Height", "Length", "Weight", "Width", "Manufacturer", "Part Number", "snap-lock", "longer neck", "UV inhibitors", "Insecticide", "Precio"]

        df = pd.DataFrame(columns=columns)
        dfs = []

        for producto in self.lista_productos:

            href, src_img, titulo_prod = producto

            if "Ytag" in titulo_prod or "Cmb" in titulo_prod or "Ear Tags" in titulo_prod or "Ear Tag" in titulo_prod:
                if "Applicator" not in titulo_prod:

                    producto = {"Imagen": src_img, "Brand": "Y-Tex"}

                    if "All American" in titulo_prod:
                        producto["Nombre"] = "All American"
                    if "Cmb Nrd" in titulo_prod:
                        producto["Quantity"] = 24

                    self.driver.get(href)

                    # precio del producto
                    # elemento_precio = WebDriverWait(self.driver, self.timeout).until(
                    #    EC.presence_of_element_located(
                    #        (By.CLASS_NAME, "price-wrapper")))
                    elemento_precio = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "css-epvm6"))
                    )

                    # Obtener el contenido del elemento (que incluye el símbolo "$" y el precio)
                    precio = elemento_precio.text
                    precio = precio.replace('\n', '').strip()
                    print(precio)
                    #########

                    # precio = elemento_precio.get_attribute("data-price-amount")
                    producto["Precio"] = precio

                    # descripcion del producto
                    elemento_descripcion = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "p.MuiTypography-root.MuiTypography-body1.css-cu1ia0")))
                    
                    # Obtiene el texto del elemento
                    texto_descripcion = elemento_descripcion.text


                    # obtener quantity
                    if "pack" in titulo_prod.lower():
                        
                        numero_split = titulo_prod.split("-")[0]
                        numero = re.findall("\d+", numero_split)[0]
                        if numero:
                            producto["Quantity"] = numero

                    if "packaging" in texto_descripcion.lower():
                        numero = re.findall("\d+", texto_descripcion)
                        if numero:
                            producto["Quantity"] = numero

                    if "packaging" in texto_descripcion.lower():
                        valor = re.findall(
                            r"Includes (\d+)", texto_descripcion)[0]
                        if valor:
                            producto["Quantity"] = numero

                    if "blank" in texto_descripcion.lower() or "blank" in titulo_prod.lower():
                        producto["Blank or Numbered"] = "Blank"

                    if "numbered" in texto_descripcion.lower() or "numbered" in titulo_prod.lower():
                        producto["Blank or Numbered"] = "Numbered"

                    texto_en_minusculas = texto_descripcion.lower() + " " + titulo_prod.lower()
                    color_names = ["red", "green", "blue", "yellow", "orange",
                                   "purple", "pink", "brown", "black", "white", "gray", "grey"]

                    first_color = (lambda colors: next(iter(colors), None))(
                        [color for color in color_names if color in texto_en_minusculas])

                    if first_color:
                        producto["Color"] = first_color

                    if "polyurethane" in texto_en_minusculas:
                        producto["Material"] = "Polyurethane"

                    if "plastic" in texto_en_minusculas:
                        producto["Material"] = "Plastic"

                    animales = ["Calves", "Cattle",
                                "Livestock", "Sheep", "Pigs", "Goats"]
                    coincidencias = [
                        animal for animal in animales if animal.lower() in texto_en_minusculas]

                    if coincidencias:
                        producto["Animal Compatibility"] = coincidencias

                    if "insecticide" in texto_en_minusculas:
                        producto["Insecticide"] = "Ok"

                    if "snap-lok" in texto_en_minusculas or "snap-lock" in texto_en_minusculas:
                        producto["snap-lock"] = "Ok"

                    df_producto = pd.DataFrame([producto])
                    dfs.append(df_producto)
                    df = pd.concat(dfs, ignore_index=True)
                    df = df.reindex(columns=columns)
        df.to_excel(filename_excel, index=False)
