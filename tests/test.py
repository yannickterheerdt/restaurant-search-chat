import pytest
from data.crud import add_restaurant_urls, add_restaurants, add_summaries
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from data.scheme import Base, RestaurantURL, RestaurantData, RestaurantContent, RestaurantSummary
from unittest.mock import patch
from config import settings
from typing import Generator

TEST_DATABASE_URL = "sqlite:///test.db"
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope='module')
def setup_database() -> Generator[None, None, None]:
    """
    Fixture to set up and tear down the test database.
    
    Creates all tables at the start of the test module and drops them after tests complete.
    """
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@patch.object(settings, 'RESTAURANT_URL', new="https://www.debuik.nl/rotterdam/zoek/restaurant/-1-stad-2-Rotterdam-1-verder-2-All-you-can-eat")
def test_add_restaurant_urls(setup_database: None) -> None:
    """
    Tests the add_restaurant_urls function to ensure it correctly adds restaurant URLs to the database.

    Verifies that two restaurants are added, with specific details for each, independent of order.

    Args:
        setup_database: Ensures the test database is set up before running.
    """
    session: Session = SessionLocal()
    add_restaurant_urls(session)

    result = session.query(RestaurantURL).all()

    # Convert the result into a dictionary keyed by restaurant name
    result_dict = {r.name: r for r in result}
    
    # Verify the expected restaurant entries
    assert len(result_dict) == 2
    assert "Shiki Sushi & Lounge" in result_dict
    assert "Rozey" in result_dict

    # Check details for each restaurant without assuming order
    assert result_dict["Shiki Sushi & Lounge"].content_url == "/rotterdam/restaurant/shiki-sushi--lounge"
    assert result_dict["Shiki Sushi & Lounge"].image_url == "https://www.debuik.nl/fp/IvIibBbUQg0BYHNHoe4v/convert?&w=2660&h=1290&fit=crop"

    assert result_dict["Rozey"].content_url == "/rotterdam/restaurant/rozey"
    assert result_dict["Rozey"].image_url == "https://www.debuik.nl/fp/vhfkMj4R4XK8zCdgCQog/convert?&w=2660&h=1290&fit=crop"
    
    session.close()

@patch.object(settings, 'RESTAURANT_URL', new="https://www.debuik.nl/rotterdam/zoek/restaurant/-1-stad-2-Rotterdam-1-verder-2-All-you-can-eat")
def test_add_restaurants(setup_database: None) -> None:
    """
    Tests the add_restaurants function to ensure it adds restaurant data and content correctly.

    Verifies that two restaurants are added with specific attributes, independent of order.
    Also verifies that RestaurantContent entries for each restaurant are created correctly.

    Args:
        setup_database: Ensures the test database is set up before running.
    """
    session: Session = SessionLocal()

    add_restaurants(session)
    
    result = session.query(RestaurantData).all()

    # Convert the result into a dictionary keyed by restaurant name
    result_dict = {r.name: r for r in result}

    # Verify the expected restaurant entries
    assert len(result_dict) == 2
    assert "Shiki Sushi & Lounge" in result_dict
    assert "Rozey" in result_dict

    # Check details for each restaurant without assuming order
    assert result_dict["Shiki Sushi & Lounge"].website_url is None
    assert result_dict["Shiki Sushi & Lounge"].instagram_url is None
    assert result_dict["Shiki Sushi & Lounge"].address == "Prins Alexanderlaan 37A 3068 PN"
    assert result_dict["Shiki Sushi & Lounge"].district == "Oost"
    assert result_dict["Shiki Sushi & Lounge"].meal_type == "Diner"
    assert result_dict["Shiki Sushi & Lounge"].restaurant_type == "Restaurant"
    assert result_dict["Shiki Sushi & Lounge"].price_level == "Betaalbaar"

    assert result_dict["Rozey"].website_url is None
    assert result_dict["Rozey"].instagram_url is None
    assert result_dict["Rozey"].address == "Wijnhaven 85 3011 WK"
    assert result_dict["Rozey"].district == "Centrum"
    assert result_dict["Rozey"].meal_type == "Lunch, Diner"
    assert result_dict["Rozey"].restaurant_type == "Restaurant"
    assert result_dict["Rozey"].price_level == "Betaalbaar"

    # Verify content without assuming order
    content_shiki = session.query(RestaurantContent).filter_by(name="Shiki Sushi & Lounge").all()
    assert len(content_shiki) == 3
    sources_shiki = {c.source for c in content_shiki}
    assert "/rotterdam/restaurant/shiki-sushi--lounge" in sources_shiki
    assert "/rotterdam/uit-eten/cocktails-slurpen-en-vis-verslinden-met-klasse-bij-shiki-sushi-lounge" in sources_shiki
    assert all("Shiki" in c.content for c in content_shiki)

    content_rozey = session.query(RestaurantContent).filter_by(name="Rozey").all()
    assert len(content_rozey) == 4
    sources_rozey = {c.source for c in content_rozey}
    assert "/rotterdam/restaurant/rozey" in sources_rozey
    assert "/rotterdam/uit-eten/vegetarisch-de-wereld-rond-bij-rozey" in sources_rozey
    assert all("Rozey" in c.content for c in content_rozey)

    session.close()

@patch.object(settings, 'RESTAURANT_URL', new="https://www.debuik.nl/rotterdam/zoek/restaurant/-1-stad-2-Rotterdam-1-verder-2-All-you-can-eat")
def test_add_summaries(setup_database: None) -> None:
    """
    Tests the add_summaries function to ensure it correctly generates and adds summaries for each restaurant.

    Verifies that summaries are created independently of order and contain the restaurant name in their content.

    Args:
        setup_database: Ensures the test database is set up before running.
    """
    session: Session = SessionLocal()

    add_summaries(session, engine)

    summaries = session.query(RestaurantSummary).all()
    
    # Convert summaries into a dictionary keyed by name
    summaries_dict = {s.name: s for s in summaries}

    # Verify expected summaries without assuming order
    assert len(summaries_dict) == 2
    assert "Rozey" in summaries_dict
    assert "Shiki Sushi & Lounge" in summaries_dict

    assert "Rozey" in summaries_dict["Rozey"].summary
    assert "Shiki" in summaries_dict["Shiki Sushi & Lounge"].summary

    session.close() 
