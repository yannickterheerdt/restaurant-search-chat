from .parser import ParserArticle, ParserRestaurant, ParserURL
from .scheme import RestaurantURL, RestaurantContent, RestaurantData, RestaurantSummary
from .summary import generate_summaries, splicegen
from config import settings

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.engine import Engine
from sqlalchemy.sql.schema import Table

import pandas as pd
import logging

from argparse import Namespace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from functools import wraps

def task_runner(task_name):
    """
    A decorator to wrap tasks with descriptive print statements.

    Args:
        task_name (str): Name of the task being executed.
    """
    def decorator(task_function):
        @wraps(task_function)
        def wrapper(*args, **kwargs):
            print(f"Starting: {task_name}...")
            try:
                task_function(*args, **kwargs)
                print(f"Completed: {task_name}.")
            except Exception as e:
                print(f"Failed: {task_name}. Error: {e}")
                raise  # Re-raise the exception for debugging or logging if needed
        return wrapper
    return decorator

@task_runner("Adding new restaurants and related content")
def add_restaurants(session: Session) -> None:
    """
    Adds new restaurants and related content to the database.

    For each restaurant in RestaurantURL that is not already in RestaurantData,
    this function retrieves restaurant data and content from external sources
    and commits them to the database.

    Args:
        session (Session): SQLAlchemy session to use for database operations.
    """
    try:
        subquery = session.query(RestaurantData.name).subquery()
        restaurants = (
            session.query(RestaurantURL)
            .filter(RestaurantURL.name.notin_(select(subquery)))
            .all()
        )

        new_data = []
        new_content = []

        for restaurant in restaurants:
            logger.info(f"Processing restaurant: {restaurant.name}")

            # Parse restaurant details
            restaurant_parser = ParserRestaurant.from_url(restaurant.content_url, restaurant.name)
            new_data.append(RestaurantData(**restaurant_parser.get_dict()))

            # Collect additional content if available
            if restaurant_parser.has_info():
                new_content.append(
                    RestaurantContent(
                        name=restaurant.name, 
                        source=restaurant.content_url, 
                        content=restaurant_parser.get_content()
                    )
                )
            
            # Add related articles
            if restaurant_parser.has_articles():
                for article_url in restaurant_parser.get_articles():
                    article_parser = ParserArticle.from_url(article_url, restaurant.name)
                    new_content.append(RestaurantContent(**article_parser.get_dict()))

        # Commit all new restaurants and content entries
        session.add_all(new_data + new_content)
        session.commit()
        logger.info(f"Added {len(new_data)} restaurants and {len(new_content)} content entries.")
    
    except Exception as e:
        logger.error(f"Error adding restaurants: {e}")
        session.rollback()

@task_runner("Adding new restaurant URLs")
def add_restaurant_urls(session: Session) -> None:
    """
    Adds new restaurant URLs to the database by parsing from an external source.

    This function retrieves a list of open restaurants, filters out any that already exist
    in the database, and commits the new URLs.

    Args:
        session (Session): SQLAlchemy session to use for database operations.
    """
    try:
        parsers = ParserURL.from_url()
        names = {name[0] for name in session.query(RestaurantURL.name).all()}

        new_urls = [
            RestaurantURL(**parser.get_dict()) 
            for parser in parsers if parser.is_open() and parser.get_dict().get('name') not in names
        ]

        session.add_all(new_urls)
        session.commit()
        logger.info(f"Added {len(new_urls)} new restaurant URLs.")

    except Exception as e:
        logger.error(f"Error adding restaurant URLs: {e}")
        session.rollback()

@task_runner("Generating and adding summaries")
def add_summaries(session: Session, engine: Engine) -> None:
    """
    Generates and adds summaries for restaurant content to the database.

    For each restaurant with content that does not already have a summary,
    this function generates a summary and commits it to the database.

    Args:
        session (Session): SQLAlchemy session to use for database operations.
        engine (Engine): SQLAlchemy engine to retrieve restaurant content data.
    """
    try:
        df = pd.read_sql('SELECT * FROM restaurantcontent', con=engine)
        df = df[df['content'].notna()]

        existing_names = {name[0] for name in session.query(RestaurantSummary.name).all()}
        df = df[~df['name'].isin(existing_names)]
        
        # Group content by restaurant name
        df_grouped = df.groupby('name')['content'].apply(' '.join).reset_index()
        maxchars = settings.MAX_TOKENS

        new_summaries = []
        for index in splicegen(maxchars, df_grouped['content'].tolist()):
            df_grouped_index = df_grouped.iloc[index]
            names = df_grouped_index['name'].tolist()
            content = df_grouped_index['content'].tolist()

            summaries = generate_summaries(content) 
            new_summaries.extend(
                [RestaurantSummary(name=name, summary=summary) for name, summary in zip(names, summaries)]
            )

        # Commit all new summaries
        session.add_all(new_summaries)
        session.commit()
        logger.info(f"Added {len(new_summaries)} summaries.")

    except Exception as e:
        logger.error(f"Error adding summaries: {e}")
        session.rollback()

def restaurant_to_dict(restaurant) -> dict:
    """
    Converts a RestaurantData object into a dictionary format for serialization.

    Args:
        restaurant (RestaurantData): The restaurant object to convert.

    Returns:
        dict: A dictionary containing restaurant attributes.
    """
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
    """
    Retrieves complete restaurant data for a list of restaurant names.

    Args:
        session (Session): SQLAlchemy session to use for database operations.
        names (list[str]): List of restaurant names to retrieve.

    Returns:
        list[dict]: A list of dictionaries, each representing a restaurant's data.
    """
    restaurants = (
        session.query(RestaurantData)
        .options(
            joinedload(RestaurantData.summary),
            joinedload(RestaurantData.restaurant_url)
        )
        .filter(RestaurantData.name.in_(names))
        .all()
    )

    # Convert each restaurant to dictionary format
    restaurant_dict = {restaurant.name: restaurant_to_dict(restaurant) for restaurant in restaurants}
    return [restaurant_dict[name] for name in names if name in restaurant_dict]
    

def get_unique_filter_values(session: Session, features: list[str]) -> dict[str, list[str]]:
    """
    Retrieves unique filter values for specified features in the RestaurantData table.

    Args:
        session (Session): SQLAlchemy session to use for database operations.
        features (list[str]): List of feature names to retrieve unique values for.

    Returns:
        dict[str, list[str]]: A dictionary where each key is a feature and the value is a list of unique values for that feature.
    """
    unique_values = {}
    for feature in features:
        try:
            raw_values = session.query(getattr(RestaurantData, feature)).distinct().all()

            # Extract, split, and clean unique values
            split_values = [
                item.strip()
                for value in raw_values if value[0] is not None
                for item in value[0].split(',')
                if item.strip()
            ]
            unique_values[feature] = sorted(set(split_values))

        except AttributeError as e:
            logger.error(f"Invalid feature '{feature}': {e}")
        except Exception as e:
            logger.error(f"Error fetching unique filter values for '{feature}': {e}")

    return unique_values

def clear_table(table: Table, engine: Engine) -> None:
    """
    Drops and recreates a specified table.

    Args:
        table (Table): SQLAlchemy table object to clear.
        engine (Engine): SQLAlchemy engine instance.
    """
    print(f"Clearing table: {table.name}")
    table.drop(engine, checkfirst=True)
    table.create(engine, checkfirst=True)

@task_runner("Clearing tables")
def clear_tables(args: Namespace, engine: Engine) -> None:
    """
    Clears tables based on the specified arguments.

    Args:
        args (Any): Parsed command-line arguments.
        engine (Engine): SQLAlchemy engine instance.
    """
    if args.add_restaurant_urls:
        clear_table(RestaurantURL.__table__, engine)

    if args.add_restaurants:
        clear_table(RestaurantData.__table__, engine)
        clear_table(RestaurantContent.__table__, engine)

    if args.add_summaries:
        clear_table(RestaurantSummary.__table__, engine)