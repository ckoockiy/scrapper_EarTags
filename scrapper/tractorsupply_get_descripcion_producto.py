import requests
from bs4 import BeautifulSoup
import pandas as pd

import time

from config import logger
import logging

class ProcesarProductosTractorSupply:

    def __init__(self, lista_urls):
        self.lista_urls = lista_urls
        self.df_tractorsupply = pd.DataFrame()

    def __verificar_encabezados(self, texto):
        resultados = []
        if "snap-lock" in texto:
            resultados.append("Ok")
        else:
            resultados.append("")
        if "longer neck" in texto:
            resultados.append("Ok")
        else:
            resultados.append("")
        if "UV inhibitors" in texto:
            resultados.append("Ok")
        else:
            resultados.append("")
        if "Insecticide" in texto:
            resultados.append("Ok")
        else:
            resultados.append("")
        return resultados

    def obtener_datos(self, url, df_final, precio, url_imagen):
        logging.info(f"Obteniendo datos de: {url}")
        # pd.set_option('display.max_columns', None)
        # Encabezado "User-Agent" personalizado que deseas enviar
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.1234.56 Safari/537.36'

        }

        # Realiza la solicitud HTTP GET con el encabezado personalizado
        response = requests.get(url, headers=headers)

        # Verifica el código de estado de la respuesta (200 significa éxito)
        if response.status_code == 200:
            time.sleep(3)
            # Parsea el contenido HTML con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encuentra la etiqueta con la clase "description-content"
            description_content = soup.find(
                'div', class_='description-content')

            if description_content:
                # Obtiene el contenido dentro de la etiqueta
                contenido = description_content.text

                # Encontrar la tabla
                table = soup.find('table')

                # Obtener las filas de la tabla
                rows = table.find_all('tr')

                # Crear una lista de encabezados
                headers = [th.text.strip() for th in rows[0].find_all('th')]

                # Crear una lista de listas para los datos
                data = []
                for row in rows[1:]:
                    cols = row.find_all('td')
                    data.append([col.text.strip() for col in cols])

                # Crear un DataFrame de Pandas
                df = pd.DataFrame(data, columns=headers)

                # Transponer el DataFrame para que los encabezados sean horizontales
                df_transposed = df.T

                # Establecer la primera fila del DataFrame transpuesto como los encabezados
                df_transposed.columns = df_transposed.iloc[0]

                # Eliminar la primera fila del DataFrame transpuesto
                df_transposed = df_transposed.iloc[1:]

                # OBTENEMOS EL NOMBRE: All-American Numbered ID Cattle Tags #
                h1_element = soup.find('h1')

                texto_dentro_de_h1 = h1_element.contents[-1].strip().split(',')[
                    0]

                ############ AGREGAR CAMPOS NUEVOS A DF ################

                df_transposed["Texto"] = contenido

                # Aplica la función a la columna 'Texto' y agrega nuevas columnas al DataFrame
                df_transposed[['snap-lock', 'longer neck', 'UV inhibitors', 'Insecticide']
                              ] = df_transposed['Texto'].apply(self.__verificar_encabezados).apply(pd.Series)

                df_transposed.insert(1, "Nombre", texto_dentro_de_h1)
                df_transposed.insert(0, "Imagen", url_imagen)
                df_transposed["Precio"] = precio

                # Lista de columnas que deseas eliminar si existen
                columns_to_remove = ['Application Method',
                                     'Country of Origin', 'Targeted Insect(s)']

                # Elimina las columnas específicas si existen en el DataFrame df
                df_transposed.drop(columns=columns_to_remove,
                                   errors='ignore', inplace=True)

                # Elimina columnas duplicadas
                df_transposed = df_transposed.loc[:, ~df_transposed.columns.duplicated(
                    keep='first')]

                # Reindexa df_final para asegurarte de que el índice sea único
                df_final = df_final.reset_index(drop=True)
                df_transposed = df_transposed.reset_index(drop=True)

                # Agregar los datos de esta página al DataFrame final
                df_final = pd.concat(
                    [df_final, df_transposed], ignore_index=True)

                return df_final

            else:
                # print(f'Problema url: {url}')
                logging.warning(f"Ha ocurrido un problema con la url: {url}")
                return False
        else:
            logging.error(f'Error al procesar URL: {url} : Código de estado: {response.status_code}')
            return False

    def url_data_to_df(self):
        logging.info("Procesando lista de urls")

        # Procesar cada URL y agregar los datos al DataFrame final
        for url in self.lista_urls:

            link = url[3]
            precio = url[1]
            url_imagen = url[2]

            result = self.obtener_datos(
                link, self.df_tractorsupply, precio, url_imagen)

            if result is not False:
                self.df_tractorsupply = result

            else:
                logging.info(f"Se intentara de nuevo con la url {link}")
                # Intentar una vez más si la función devuelve False
                result = self.obtener_datos(
                    link, self.df_tractorsupply, precio, url_imagen)
                if result is not False:
                    self.df_tractorsupply = result

        # Elimina las columnas específicas si existen en el DataFrame df
        columns_to_remove = ['Warranty', 'Country of Origin', 'Texto']
        self.df_tractorsupply.drop(columns=columns_to_remove,
                                   errors='ignore', inplace=True)

        # Eliminar las columnas que esten despues de la columna precio
        self.df_tractorsupply = self.df_tractorsupply.loc[:, :'Precio']

        # remover algunas palabras de headers
        self.df_tractorsupply = self.df_tractorsupply.rename(columns=lambda x: x.replace('Product ', '').replace(
            'Primary ', '').replace('Package ', '').replace(' Design', ''), inplace=False)

        # Imprimir el DataFrame final
        print(self.df_tractorsupply)

        # guardar df en excel
        writer = pd.ExcelWriter('pandas_image.xlsx', engine='xlsxwriter')

        self.df_tractorsupply.to_excel(
            writer, sheet_name='Sheet1', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Insert an image.
        # worksheet.insert_image('D3', 'logo.jpg', {"x_scale": 0.3, "y_scale": 0.3})

        writer.close()
