import logging

logging.basicConfig(
    filename='logs/scrapper.log',
    encoding='utf-8',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M',
    level=logging.INFO
)

