from sqlalchemy import Column, String, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()

class RestaurantData(Base):
    __tablename__ = "restaurantdata"
    
    name = Column(String, primary_key = True)
    website_url = Column(String)
    instagram_url = Column(String)
    address = Column(String)
    meal_type = Column(String)
    district = Column(String)
    restaurant_type = Column(String)
    price_level = Column(String)
    
    # One-to-One Relationship with RestaurantURL
    restaurant_url = relationship("RestaurantURL", back_populates="restaurant_data", uselist=False)
    
    # One-to-Many Relationship with RestaurantContent
    contents = relationship("RestaurantContent", back_populates="restaurant_data")

    # One-to-One Relationship with RestaurantSummary
    summary = relationship("RestaurantSummary", back_populates="restaurant_data", uselist=False)

class RestaurantURL(Base):
    __tablename__ = "restauranturl"

    name = Column(String, ForeignKey('restaurantdata.name'), primary_key=True)
    content_url = Column(String)
    image_url = Column(String)

    # Back reference to RestaurantData
    restaurant_data = relationship("RestaurantData", back_populates="restaurant_url")
  
class RestaurantContent(Base):
    __tablename__ = "restaurantcontent"

    name = Column(String, ForeignKey('restaurantdata.name'), primary_key=True)  # ForeignKey to RestaurantData
    source = Column(String, primary_key=True)
    content = Column(String)

    # Back reference to RestaurantData
    restaurant_data = relationship("RestaurantData", back_populates="contents")

class RestaurantSummary(Base):
    __tablename__ = "restaurantsummary"

    name = Column(String, ForeignKey('restaurantdata.name'), primary_key=True)  # ForeignKey to RestaurantData
    summary = Column(String)

    # Back reference to RestaurantData
    restaurant_data = relationship("RestaurantData", back_populates="summary")

engine = create_engine('sqlite:///restaurants.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
