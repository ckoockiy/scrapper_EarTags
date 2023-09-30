from bs4 import BeautifulSoup
import requests
from user_agent import generate_user_agent
import re


import pandas as pd


class AgrisupplyScraper:
    def __init__(self):
        self.url = "https://www.agrisupply.com/search.aspx?ss=ear+tags"
        self.datos_productos = []
        self.headers = {
            'User-Agent': generate_user_agent(),
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

    def get_all_products(self):

        r = requests.get(self.url, headers=self.headers)

        # Parsea el HTML con BeautifulSoup
        soup = BeautifulSoup(r.content, 'html.parser')

        # Encuentra todos los elementos div con la clase "product-grid-item p-2 p-md-3"
        divs = soup.find_all('div', class_='product-grid-item p-2 p-md-3')

        # Itera a través de los divs y extrae la información deseada
        valores_producto = []
        for div in divs:
            imagen = div.find('img')['src']
            nombre_producto = div.find('span', class_='product-name').text
            precio = div.find('span', class_='hidden hidden-price').text

            url_producto = div.find('a', class_='d-block gtm-product-click')
            enlace = url_producto.get('href')

            if "Ear Tags" in nombre_producto or "EAR TAGS" in nombre_producto:

                print("Imagen:", imagen)
                print("Nombre del Producto:", nombre_producto)
                print("Enlace:", enlace)
                print("Precio:", precio)

                valor = nombre_producto.split("Ear Tags")
                if len(valor) == 2:

                    cantidad = re.findall(r'\d+', valor[1])
                    print(f"Cantidad: {cantidad[0]}")

                valores_producto = [imagen, nombre_producto,
                                    enlace, precio, cantidad[0]]

                if nombre_producto == "DUFLEX EAR TAGS":
                    print(f"Cantidad: 24")
                    marca_nombre = "DUFLEX"
                    print(f"Marca: {marca_nombre}")

                    valores_producto.append(marca_nombre)

                # marca y nombre
                marca_nombre = nombre_producto.split("®")
                if len(marca_nombre) == 2:
                    print(f"Marca: {marca_nombre[0]}")
                    valores_producto.append(marca_nombre[0])
                if len(marca_nombre) == 3:
                    print(f"Marca: {marca_nombre[0]}")
                    print(f"Nombre: {marca_nombre[1]}")
                    valores_producto.append(marca_nombre[0])
                    valores_producto.append(marca_nombre[1])

                print("\n")
                self.datos_productos.append(valores_producto)

    def __obtener_medidas(self, texto):
        # Patrón regex para buscar las medidas en ambos formatos
        patron = r'Size:\s*(\d+\s*\d*\/\d*")\s*(?:Length\s*x\s*)?(\d+\s*\d*\/\d*")?\s*Width(?:\s*x\s*(\d+\s*\d*\/\d*")\s*Height)?'

        matches = re.search(patron, texto)
        if matches:
            medidas = [m.strip('"') for m in matches.groups() if m]
            return medidas
        else:
            return None

    def get_data_product(self):
        columns = ["Imagen", "Brand", "Nombre", "1-Piece or 2-Piece", "Animal Compatibility", "Blank or Numbered", "Letter or Number Size", "Quantity", "Color",
                   "Material", "Height", "Length", "Weight", "Width", "Manufacturer", "Part Number", "snap-lock", "longer neck", "UV inhibitors", "Insecticide", "Precio"]

        df = pd.DataFrame(columns=columns)
        dfs = []

        for datos in self.datos_productos:

            r = requests.get(datos[2], headers=self.headers)
            soup = BeautifulSoup(r.content, 'html.parser')

            if r.ok:
                
                producto = {"Imagen": datos[0], "Precio": datos[3], "Quantity": datos[4], "Brand": datos[5]}
                if len(datos) == 7:
                    producto["Nombre"] = datos[6]
                
                if "insecticide" in datos[1].lower():
                    producto["Insecticide"] = "Ok"
                # Descripcion
                div_product_desc = soup.find(
                    'div', class_='product-description mt-2')

                animales = ["Calves", "Cattle",
                            "Livestock", "Sheep", "Pigs", "Goats"]

                for div_prod in div_product_desc:

                    texto_div = div_prod.text.strip()

                    coincidencias = [
                        animal for animal in animales if animal.lower() in str(texto_div).lower()]

                    if coincidencias:
                        producto["Animal Compatibility"] = coincidencias

                    if "polyurethane" in texto_div.lower():
                        producto["Material"] = "Polyurethane"

                    if "plastic" in texto_div.lower():
                        producto["Material"] = "Plastic"

                # Descipcion 2
                div_product_overview = soup.find('div', class_='col-md-8')

                # Encuentra todos los elementos 'li' dentro del div
                list_items = div_product_overview.find_all('li')

                # Recorre los elementos 'li' y obtén su contenido
                for li in list_items:
                    
                    texto_li = li.text.strip()

                    if "Size" in texto_li:

                        medidas = self.__obtener_medidas(texto_li)

                        if "Length" in texto_li:
                            producto["Length"] = medidas[0]
                            producto["Width"] = medidas[1]
                        else:
                            producto["Width"] = medidas[0]
                            producto["Height"] = medidas[1]

                    if "Color" in texto_li:
                        color = texto_li.split(" ")
                        producto["Color"] = color[1]

                    if "Snap-Lok" in texto_li:
                        producto["snap-lock"] = "Ok"

                    if "blank" in texto_li.lower() or "blank" in datos[1].lower():
                        producto["Blank or Numbered"] = "Blank"

                    if "numbered" in texto_li.lower():
                        producto["Blank or Numbered"] = "Numbered"
                
                df_producto = pd.DataFrame([producto])
                dfs.append(df_producto)
                #df = df.append(producto, ignore_index=True)
                df = pd.concat(dfs, ignore_index=True)
                df = df.reindex(columns=columns)
        
        return df
