from scrapper.tractorsupply_scrapping import TractorSupplyScraper
from scrapper.tractorsupply_get_descripcion_producto import ProcesarProductosTractorSupply
from scrapper.ruralking.ruralking_scrapping import RuralkingScrapper
from scrapper.agrisupply.agrisupply_scrapping import AgrisupplyScraper
from scrapper.runnings.runnings_scrapping import RunningsScrapper

# Proceso TractorSupply
scraper = TractorSupplyScraper()
lista_urls_productos = scraper.scrape_and_close("https://www.tractorsupply.com/tsc/catalog/ear-tags?")
procesadorProductosTractorSupply = ProcesarProductosTractorSupply(lista_urls_productos)
procesadorProductosTractorSupply.url_data_to_df("/home/koki/Pictures/projects-python/scrapper-mario/TractorSupply.xlsx")



# Proceso agrisupply
agrisupply = AgrisupplyScraper()
agrisupply.get_all_products()
agrisupply.process_data_to_df('/home/koki/Pictures/projects-python/scrapper-mario/agrisupply.xlsx')

# Proceso ruralking
ruralking = RuralkingScrapper()
ruralking.obtener_datos_ruralking()
ruralking.process_data_to_df('/home/koki/Pictures/projects-python/scrapper-mario/ruralking.xlsx')

# Proceso runnings
runnings = RunningsScrapper()
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

for url in lista_urls:
    runnings.get_data_product(url)
runnings.process_data_to_df('/home/koki/Pictures/projects-python/scrapper-mario/runnings.xlsx')
