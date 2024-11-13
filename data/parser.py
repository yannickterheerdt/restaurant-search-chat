from parsel import Selector
from .webdriver import get_page_source_urls, get_page_source_restaurant

def join_strings(strs: list[str]) -> str | None:
    """Joins a list of strings, ignoring None values. Returns None if all values are None."""
    result = ' '.join(s for s in strs if s is not None)
    return result if result else None

def get_text_from_xpath(content: Selector, query: str, sep: str = ' ') -> str | None:
    """Retrieves text content based on an XPath query, joining multiple results with a separator if needed."""
    response = content.xpath(query).getall()
    if not response:
        return None
    return sep.join(response) if sep else response


class ParserRestaurant:
    """
    Parses restaurant data from a restaurant page, extracting various details like address, tags, and contact info.
    """

    @classmethod
    def from_url(cls, url: str, name: str) -> "ParserRestaurant":
        page_source = Selector(get_page_source_restaurant(url))
        return cls(page_source, name)

    def __init__(self, page_source: Selector, name: str):
        self.content = page_source
        self.name = name

    def get_address(self) -> str | None:
        street = get_text_from_xpath(self.content, "//div[@class='address']/span[@class='street']/text()")
        postalcode = get_text_from_xpath(self.content, "//div[@class='address']/span[@class='postcode']/text()")
        return join_strings([street, postalcode])

    def get_tags(self) -> str | None:
        tags = get_text_from_xpath(self.content, "//div[@class='page-section-tags']/a[@class='btn-tag-large']/text()", sep=', ')
        return f"Labels: {tags}." if tags else None

    def get_website(self) -> str | None:
        return get_text_from_xpath(self.content, "//div[@class='restaurant-contact']//div[@class='website']//div[@class='show']/a/@href")

    def get_instagram(self) -> str | None:
        return get_text_from_xpath(self.content, "//div[@class='restaurant-contact']//li[@class='instagram']/a/@href")

    def get_info(self) -> str | None:
        introtext = get_text_from_xpath(self.content, "//div[@class='introductie']/p/text()")
        description = get_text_from_xpath(self.content, "//div[@class='omschrijving']/p/text()")
        return join_strings([introtext, description])

    def has_info(self) -> bool:
        return self.get_info() is not None

    def get_content(self) -> str | None:
        info = self.get_info()
        tags = self.get_tags()
        return join_strings([info, tags])

    def get_articles(self) -> list[str]:
        articles = get_text_from_xpath(self.content, "//div[@class='verhalen-item']//div[@class='item-image']//a//@href", sep=None)
        return articles if articles else []

    def has_articles(self) -> bool:
        return bool(self.get_articles())

    def get_features(self) -> dict[str, str]:
        features = get_text_from_xpath(self.content, "//div[contains(@class,'content')]/dl/dt/text()", sep=None)
        
        values = []
        for dd in self.content.xpath("//div[contains(@class,'content')]/dl/dd"):
            value = get_text_from_xpath(dd, ".//text()", sep=' ')
            values.append(value if value is not None else '')

        if features is None or not values:
            return {}
        
        return {features[i]: values[i] for i in range(len(features))}

    def get_dict(self) -> dict[str, str | None]:
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
    """
    Parses content from an article page related to a restaurant.
    """

    @classmethod
    def from_url(cls, url: str, name: str) -> "ParserArticle":
        page_source = Selector(get_page_source_restaurant(url))
        return cls(page_source, url, name)

    def __init__(self, page_source: Selector, url: str, name: str):
        self.content = page_source
        self.name = name
        self.source = url

    def get_content(self) -> str | None:
        text = get_text_from_xpath(self.content, "//div[@class='content']//p/text()")
        title = get_text_from_xpath(self.content, "//div[@class='title']//h1/text()")
        subtitles = get_text_from_xpath(self.content, "//div[@class='content']//h2[@class = 'p1']/text()", sep='. ')
        return join_strings([text, subtitles, title])

    def get_dict(self) -> dict[str, str | None]:
        return {
            'name': self.name,
            'source': self.source,
            'content': self.get_content()
        }


class ParserURL:
    """
    Parses URLs from a page listing restaurants, extracting relevant metadata for each.
    """

    @classmethod
    def from_url(cls) -> list["ParserURL"]:
        page_source = Selector(get_page_source_urls())
        return [cls(r) for r in page_source.xpath("//div[@class='resultaat']")]

    def __init__(self, page_source: Selector):
        self.content = page_source

    def is_open(self) -> bool:
        closed = self.content.xpath(".//div[@class='label-tijdelijk']") or self.content.xpath(".//div[@class='label-permanent']")
        return not closed

    def get_name(self) -> str | None:
        return self.content.xpath(".//a[@class='title']/text()").get()

    def get_url(self) -> str | None:
        return self.content.xpath(".//div[contains(@class, 'item-info')]//a[contains(@class, 'title')]/@href").get()

    def get_image_url(self) -> str | None:
        return self.content.xpath(".//div[@class='item-image']/a/img/@src").get()

    def get_dict(self) -> dict[str, str | None]:
        return {
            'name': self.get_name(),
            'content_url': self.get_url(),
            'image_url': self.get_image_url()
        }
