from parsel import Selector
from .webdriver import get_page_source_urls, get_page_source_restaurant
    
def join_strings(strs: list[str]) -> str | None:
    has_non_none = any(x is not None for x in strs)
    if has_non_none:
        return ' '.join(s for s in strs if s is not None)
    else:
        return None
        
def get_query(content: Selector, query: str, sep: str = ' ') -> str | list[str] | None:
    response = content.xpath(query).getall()
    if not response:
        return None
    
    if sep:
        return sep.join(response)
    else: 
        return response
    
class ParserRestaurant:

    @classmethod
    def from_url(cls, url, name):
        page_source = Selector(get_page_source_restaurant(url))
        return cls(page_source, name)

    def __init__(self, page_source: Selector, name):
        self.content = page_source
        self.name = name
    
    def get_address(self):
        street = get_query(self.content, "//div[@class='address']/span[@class='street']/text()")
        postalcode = get_query(self.content, "//div[@class='address']/span[@class='postcode']/text()")
        return join_strings([street, postalcode])
    
    def get_tags(self):
        return 'Labels: ' + get_query(self.content, "//div[@class='page-section-tags']/a[@class='btn-tag-large']/text()", sep = ', ') + '.'
    
    def get_website(self):
        return get_query(self.content, "//div[@class='restaurant-contact']//div[@class='website']//div[@class='show']/a/@href")
    
    def get_instagram(self):
        return get_query(self.content, "//div[@class='restaurant-contact']//li[@class='instagram']/a/@href")
    
    def get_info(self):
        introtext = get_query(self.content, "//div[@class='introductie']/p/text()")
        description = get_query(self.content, "//div[@class='omschrijving']/p/text()")
        return join_strings([introtext, description])
    
    def has_info(self):
        return self.get_info() is not None
    
    def get_content(self):
        info = self.get_info()
        tags = self.get_tags()
        return join_strings([info, tags])
    
    def get_articles(self):
        return get_query(self.content, "//div[@class='verhalen-item']//div[@class='item-image']//a//@href", sep = None)
    
    def has_articles(self):
        return self.get_articles() is not None
    
    def get_features(self):
        features = get_query(self.content, "//div[contains(@class,'kenmerken')]/div[contains(@class,'content')]/dl/dt/text()", sep = None)
        values = get_query(self.content, "//div[contains(@class,'kenmerken')]/div[contains(@class,'content')]/dl/dd/text()", sep = None)
        
        if features is None or values is None:
            return {}
        
        return {features[i]: values[i] for i in range(len(values))}
    
    def get_dict(self):
        features = self.get_features()
        
        return {
            'name': self.name,
            'website_url': self.get_website(),
            'instagram_url': self.get_instagram(),
            'address': self.get_address(),
            'meal_type': features.get('Maaltijd'),
            'district': features.get('Stadsdeel'),
            'restaurant_type': features.get('Soort zaak'),
            'price_level': features.get('Prijsniveau')
        }
    
class ParserArticle:
    
    @classmethod
    def from_url(cls, url, name):
        page_source = Selector(get_page_source_restaurant(url))
        return cls(page_source, url, name)

    def __init__(self, page_source: Selector, url, name):
        self.content = page_source
        self.name = name
        self.source = url

    def get_content(self):
        text = get_query(self.content, "//div[@class='content']//p/text()")
        title = get_query(self.content, "//div[@class='title']//h1/text()")
        subtitles = get_query(self.content, "//div[@class='content']//h2[@class = 'p1']/text()", sep = '. ')

        return join_strings([text, subtitles, title])
    
    def get_dict(self):
        return {
            'name': self.name,
            'source': self.source,
            'content': self.get_content()
        }

class ParserURL:

    @classmethod
    def from_url(cls):
        page_source = Selector(get_page_source_urls())
        return [cls(r) for r in page_source.xpath("//div[@class='resultaat']")]
    
    def __init__(self, page_source: Selector):
        self.content = page_source
    
    def is_open(self):
        closed = self.content.xpath(".//div[@class='label-tijdelijk']") or self.content.xpath(".//div[@class='label-permanent']") 
        return not closed
    
    def get_name(self):
        return self.content.xpath(".//a[@class='title']/text()").get()
    
    def get_url(self):
        return self.content.xpath(".//div[contains(@class, 'item-info')]//a[contains(@class, 'title')]/@href").get()
    
    def image_url(self):
        return self.content.xpath(".//div[@class='item-image']/a/img/@src").get()
    
    def get_dict(self):
        return {
            'name': self.get_name(),
            'content_url': self.get_url(),
            'image_url': self.image_url()
        }
    




    

