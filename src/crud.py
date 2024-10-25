from .parser import ParserArticle, ParserRestaurant, ParserURL
from .data import RestaurantURL, RestaurantContent, RestaurantData, RestaurantSummary
from .summary import generate_summaries, splicegen
from config import settings

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

import pandas as pd

def add_restaurants(session: Session) -> None:
    subquery = session.query(RestaurantData.name).subquery()
    restaurants = session.query(RestaurantURL).filter(RestaurantURL.name.notin_(select(subquery))).all()
    for restaurant in restaurants:
        print(restaurant.name)
        parser = ParserRestaurant.from_url(restaurant.content_url, restaurant.name)
        session.add(RestaurantData(**parser.get_dict()))
        if parser.has_info():
            session.add(RestaurantContent(name=restaurant.name, source=restaurant.content_url, content=parser.get_content()))
        if parser.has_articles():
            for article_url in parser.get_articles():
                parser = ParserArticle.from_url(article_url, restaurant.name)
                session.add(RestaurantContent(**parser.get_dict()))
    
        session.commit()      

def add_restaurant_urls(session: Session) -> None:
    parsers = ParserURL.from_url()
    restaurantURLs = [RestaurantURL(**parser.get_dict()) for parser in parsers if parser.is_open()]
    names = session.query(RestaurantURL.name).all()
    names = {name[0] for name in names}
    restaurantURLs = [url for url in restaurantURLs if url.name not in names]
    session.add_all(restaurantURLs)
    session.commit()

def add_summaries(session: Session, engine: Engine) -> None:
    df = pd.read_sql(f'SELECT * FROM restaurantcontent', con=engine)
    df = df[df['content'].notna()]
    names = session.query(RestaurantSummary.name).all()
    names = {name[0] for name in names}
    df = df[~df['name'].isin(names)]
    df_grouped = df.groupby('name')['content'].apply(' '.join).reset_index()

    maxchars = settings.MAX_TOKENS
    for index in splicegen(maxchars, df_grouped['content'].tolist()):
        df_grouped_index = df_grouped.iloc[index]
        names = df_grouped_index['name'].tolist()
        content =  df_grouped_index['content'].tolist()
        summaries = generate_summaries(content) 
        session.add_all([RestaurantSummary(name=name, summary=summary) for name, summary in zip(names, summaries)])
        session.commit()
