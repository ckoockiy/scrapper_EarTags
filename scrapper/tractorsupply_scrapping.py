from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
from user_agent import generate_user_agent
import re


class TractorSupplyScraper:
    def __init__(self):
        self.driver = None
        self.lista_info = []

    def start_driver(self):
        chrome_options = webdriver.ChromeOptions()
        custom_headers = {
            "User-Agent": generate_user_agent(),
        }
        for header, value in custom_headers.items():
            chrome_options.add_argument(f"--{header}={value}")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def scroll_down(self, times):
        for _ in range(times):
            self.driver.find_element(
                By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            sleep(1)

    def get_products(self):

        timeout = 20

        try:
            # Espera a que el elemento con la clase "grid-container" sea visible
            grid_container = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "grid-container")))

            # Busca todos los elementos "div" con la clase "grid-inner" dentro de "grid-container"
            grid_inner_divs = grid_container.find_elements(
                By.CLASS_NAME, "grid-inner")

            # Itera a través de los elementos "grid-inner" encontrados
            for grid_inner in grid_inner_divs:
                # Encuentra la etiqueta <img> dentro de cada "grid-inner"
                img_element = grid_inner.find_element(By.TAG_NAME, "img")
                a_element = grid_inner.find_element(By.TAG_NAME, "a")

                # Encuentra el elemento con atributo "itemprop='price'" dentro de "grid-inner"
                precio_element = grid_inner.find_element(
                    By.XPATH, './/div[@itemprop="price"]')

                # Obtiene el precio del elemento
                precio = precio_element.text.strip()

                # Obtiene el valor del atributo "src" de la etiqueta <img>
                link_imagen = img_element.get_attribute("src")
                alt_text = img_element.get_attribute("alt")
                url_producto = a_element.get_attribute("href")

                if "Cattle Tags" in alt_text or "Ear Tags" in alt_text:
                    self.lista_info.append(
                        [alt_text, precio, link_imagen, url_producto])

            # return self.lista_info
        except Exception as e:
            print("Error durante la obtención de productos:", str(e))
            # return []

    def get_pagination_count(self):
        # Espera a que los elementos de paginación sean visibles
        pagination_elements = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@aria-label, 'Page') or contains(@id, 'paginationSelect_')]"))
        )

        # Filtra los elementos de paginación utilizando expresiones regulares
        pagination_elements = [element for element in pagination_elements if re.search(
            r"Page \d+|paginationSelect_\d+", element.get_attribute("aria-label") + element.get_attribute("id"))]

        # Cuenta cuántos elementos de paginación se encontraron
        numero_de_paginaciones = len(pagination_elements)

        return numero_de_paginaciones

    def scrape_tractorsupply(self, url):

        try:
            self.start_driver()
            self.driver.get(url)

            # Definir el tiempo máximo de espera en segundos
            timeout = 15

            if self.driver.title == "Access Denied":
                print("El título de la página es:", self.driver.title)

            self.scroll_down(30)  # Realiza 30 scrolls

            # obtener cantidad de paginaciones
            numero_de_paginaciones = self.get_pagination_count()

            for pagina in range(2, int(numero_de_paginaciones)+1):
                # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                self.scroll_down(30)  # Realiza 30 scrolls

                # Espera hasta que se carguen los elementos de paginación
                pagination_elements1 = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, f"//a[contains(@id, 'paginationSelect_{pagina}')]"))
                )

                # OBTENER PRODUCTOS
                self.get_products()

                for p_element in pagination_elements1:
                    p_element.click()
                    sleep(5)
                    print("PAGINA", self.driver.current_url)

            return self.lista_info

        except Exception as e:
            print("Error durante el proceso:", str(e))
            return []

    def scrape_and_close(self, url):
        data = self.scrape_tractorsupply(url)
        self.close_driver()
        return data
