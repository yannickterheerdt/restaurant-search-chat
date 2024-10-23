import pytest
from src.crud import add_restaurant_urls, add_restaurants, add_summaries
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.data import Base, RestaurantURL, RestaurantData, RestaurantContent, RestaurantSummary
from unittest.mock import patch
from config import settings

TEST_DATABASE_URL = "sqlite:///test.db"
engine = create_engine(TEST_DATABASE_URL)
Session = sessionmaker(bind=engine)

@pytest.fixture(scope='module')
def setup_database():
    # Create tables in the test database
    Base.metadata.create_all(engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(engine)

@patch.object(settings, 'RESTAURANT_URL', new="https://www.debuik.nl/rotterdam/zoek/restaurant/-1-stad-2-Rotterdam-1-verder-2-All-you-can-eat")
def test_add_restaurant_urls(setup_database):
    session = Session()
    add_restaurant_urls(session)

    result = session.query(RestaurantURL).all()

    assert len(result) == 2

    assert result[0].name == "Shiki Sushi & Lounge"
    assert result[0].content_url == "/rotterdam/restaurant/shiki-sushi--lounge"
    assert result[0].image_url == "https://www.debuik.nl/fp/IvIibBbUQg0BYHNHoe4v/convert?&w=2660&h=1290&fit=crop"

    assert result[1].name == "Rozey"
    assert result[1].content_url == "/rotterdam/restaurant/rozey"
    assert result[1].image_url == "https://www.debuik.nl/fp/vhfkMj4R4XK8zCdgCQog/convert?&w=2660&h=1290&fit=crop"

    session.close()

@patch.object(settings, 'RESTAURANT_URL', new="https://www.debuik.nl/rotterdam/zoek/restaurant/-1-stad-2-Rotterdam-1-verder-2-All-you-can-eat")
def test_add_restaurants(setup_database):
    session = Session()

    add_restaurants(session)
    
    result = session.query(RestaurantData).all()

    assert len(result) == 2

    assert result[0].name == "Shiki Sushi & Lounge"
    assert result[0].website_url is None
    assert result[0].instagram_url is None
    assert result[0].address == "Prins Alexanderlaan 37A 3068 PN"
    assert result[0].district == "Oost"
    assert result[0].meal_type == "Diner"
    assert result[0].restaurant_type == "Restaurant"
    assert result[0].price_level == "Betaalbaar"

    assert result[1].name == "Rozey"
    assert result[1].website_url is None
    assert result[1].instagram_url is None
    assert result[1].address == "Wijnhaven 85 3011 WK"
    assert result[1].district == "Centrum"
    assert result[1].meal_type == "Lunch, Diner"
    assert result[1].restaurant_type == "Restaurant"
    assert result[1].price_level == "Betaalbaar"

    content = session.query(RestaurantContent).filter_by(name="Shiki Sushi & Lounge").all()
    assert len(content) == 3
    sources = [c.source for c in content]
    assert "/rotterdam/restaurant/shiki-sushi--lounge" in sources
    assert "/rotterdam/uit-eten/cocktails-slurpen-en-vis-verslinden-met-klasse-bij-shiki-sushi-lounge" in sources
    assert all("Shiki" in c.content for c in content)

    content = session.query(RestaurantContent).filter_by(name="Rozey").all()
    assert len(content) == 4
    sources = [c.source for c in content]
    assert "/rotterdam/restaurant/rozey" in sources
    assert "/rotterdam/uit-eten/vegetarisch-de-wereld-rond-bij-rozey" in sources
    assert all("Rozey" in c.content for c in content)

    session.close()

def test_add_summaries(setup_database):
    session = Session()

    add_summaries(session, engine)

    summaries = session.query(RestaurantSummary).all()
    
    assert len(summaries) == 2 

    assert summaries[0].name == "Rozey"
    assert "Rozey" in summaries[0].summary

    assert summaries[1].name == "Shiki Sushi & Lounge"
    assert "Shiki" in summaries[1].summary

    session.close() 

