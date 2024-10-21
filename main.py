from src.crud import *
from src.data import Session, engine
import argparse

def main():
    parser = argparse.ArgumentParser(description="Control which functions to call.")
    parser.add_argument('--add_restaurant_urls', action='store_true', help='Call add_restaurant_urls function')
    parser.add_argument('--add_restaurants', action='store_true', help='Call add_restaurants function')
    parser.add_argument('--add_summaries', action='store_true', help='Call add_summaries function')
    
    args = parser.parse_args()
    
    session = Session()
    
    if args.add_restaurant_urls:
        add_restaurant_urls(session)
    if args.add_restaurants:
        add_restaurants(session)
    if args.add_summaries:
        add_summaries(session, engine)
    
    session.close()

if __name__ == "__main__":
    main()