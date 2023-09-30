from scrapper.tractorsupply_scrapping import TractorSupplyScraper
from scrapper.tractorsupply_get_descripcion_producto import ProcesarProductosTractorSupply
from scrapper.ruralking.ruralking_scrapping import RuralkingScrapper
from scrapper.agrisupply.agrisupply_scrapping import AgrisupplyScraper
from scrapper.runnings.runnings_scrapping import RunningsScrapper


# Uso de la clase
# scraper = TractorSupplyScraper()
# lista_datos = scraper.scrape_and_close("https://www.tractorsupply.com/tsc/catalog/ear-tags?")

# url_data_to_df(lista_datos)
# procesadorProductosTractorSupply = ProcesarProductosTractorSupply(lista_datos)
# procesadorProductosTractorSupply.url_data_to_df()


"""
    DATOS OBTENIDOS CON SELENIUM
    Y-TEX All-American Numbered ID Cattle Tags, 2 pc., 176-200, Large, Blue, 25-Pack, 7908176
    Precio: $34.99
    imagen de src: https://media.tractorsupply.com/is/image/TractorSupplyCompany/1164194?$456$
    URL  https://www.tractorsupply.com/tsc/product/y-tex-all-american-blue-id-tag-2-piece-large-nbr-176-200-pack-of-25
"""


'''
# Proceso agrisupply
agrisupply = AgrisupplyScraper()
agrisupply.get_all_products()
df_agrisupply = agrisupply.get_data_product()
print(df_agrisupply)

# Proceso ruralking
ruralking = RuralkingScrapper()
ruralking.obtener_datos_ruralking()
df_ruralking = ruralking.procesar_producto()

print(df_ruralking)

'''

runnings = RunningsScrapper()
'''
url = 'https://www.runnings.com/search.html?query=ear+tags&page=1'

lista_urls = []

runnings.requests_url(url)
num_paginas = runnings.count_pagination_tiles()
runnings.close_popup()
urls = runnings.get_product_urls()
lista_urls.extend(urls)

for i in range(num_paginas, num_paginas+num_paginas):
    runnings.requests_url(
        f'https://www.runnings.com/search.html?query=ear+tags&page={i}')
    runnings.close_popup()
    urls = runnings.get_product_urls()
    lista_urls.extend(urls)

# print(lista_urls)
'''

#for url in lista_urls:
lista_urls = [
    "https://www.runnings.com/dominator-insecticide-tag-20s-3950979.html",
    "https://www.runnings.com/tri-zap-insecticide-tag-20pk-63715044.html",
    "https://www.runnings.com/y-texr-pythonr-insecticide-ear-tag-20-pack.html",
    "https://www.runnings.com/y-texr-all-american-ear-tag-51-76-sheepstar-25-pack-yellow.html"


]
for url in lista_urls:
    runnings.get_data_product(url)
runnings.process_data_to_df('runnings.xlsx')


#df_runnings.to_excel('runnings.xlsx', index=False)
