from .parser import ParserArticle, ParserRestaurant, ParserURL
from .scheme import RestaurantURL, RestaurantContent, RestaurantData, RestaurantSummary
from .summary import generate_summaries, splicegen
from config import settings

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
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

def restaurant_to_dict(restaurant):
    return {
        "name": restaurant.name,
        "website_url": restaurant.website_url,
        "instagram_url": restaurant.instagram_url,
        "address": restaurant.address,
        "meal_type": restaurant.meal_type,
        "district": restaurant.district,
        "restaurant_type": restaurant.restaurant_type,
        "price_level": restaurant.price_level,
        "summary": restaurant.summary.summary if restaurant.summary else None,
        "image_url": restaurant.restaurant_url.image_url if restaurant.restaurant_url else None,
        "content_url": restaurant.restaurant_url.content_url if restaurant.restaurant_url else None,
    }

def get_complete_restaurant_data(session: Session, names: list[str]) -> list[dict]:
    restaurants = (
        session.query(RestaurantData)
        .options(
            joinedload(RestaurantData.summary),
            joinedload(RestaurantData.restaurant_url)
        )
        .filter(RestaurantData.name.in_(names))
        .all()
    )

    restaurant_dict = {restaurant.name: restaurant_to_dict(restaurant) for restaurant in restaurants}

    return [restaurant_dict[name] for name in names if name in restaurant_dict]
    

def get_unique_filter_values(session: Session, features: list[str]) -> dict[str, list[str]]:
    unique_values = {}
    for feature in features:
        # Query distinct values for each feature
        raw_values = session.query(getattr(RestaurantData, feature)).distinct().all()
        
        # Flatten, split by ', ', remove None and '' values, and strip whitespace
        split_values = [
            item.strip()  # Remove any surrounding whitespace
            for value in raw_values if value[0] is not None
            for item in value[0].split(',')  # Split by comma
            if item.strip()  # Exclude empty strings after stripping
        ]
        
        # Get unique values and sort them
        unique_values[feature] = sorted(set(split_values))

    return unique_values