
CHROMEDRIVE_PATH = './chromedriver/chromedriver.exe'

RESTAURANT_URL = 'https://www.debuik.nl/rotterdam/zoek/restaurant/-1-stad-2-Rotterdam'

BASE_URL = 'https://www.debuik.nl'

OPENAI_API_KEY = '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'

OPENAI_ENGINE = 'gpt-4o-mini'

MAX_TOKENS = 200000

PROMPT_SUMMARY_TEMPLATE = """Geef een samenvatting van de volgende informatie over een restaurant of bar. Deze samenvatting moet gebruikt kunnen worden in een applicatie om verzoeken van mensen te koppelen aan potentiële restaurants of bars. 
            De samenvatting moet de volgende elementen bevatten: 
            - Type keuken (bijvoorbeeld Italiaans, Thais, etc.) of type bar (borrelen, cocktails, uitgaan, etc.)
            - Locatie 
            - Unieke kenmerken of specialiteiten 
            - Algemene sfeer
            - Prijsniveau (zonder exacte prijzen te noemen)
            - Doelgroep (bijvoorbeeld gezinnen, studenten, zakelijke bijeenkomsten, etc.)
            Zorg ervoor dat de samenvatting kort en bondig is, bij voorkeur in één alinea."""


