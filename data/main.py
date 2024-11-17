from .crud import *
from .scheme import *
import argparse

def main():
    # Define the command-line arguments
    parser = argparse.ArgumentParser(description="Control database operations.")
    parser.add_argument('--clear_tables', action='store_true', help='Clear specified tables in the database')
    parser.add_argument('--add_restaurant_urls', action='store_true', help='Call add_restaurant_urls function')
    parser.add_argument('--add_restaurants', action='store_true', help='Call add_restaurants function')
    parser.add_argument('--add_summaries', action='store_true', help='Call add_summaries function')
    args = parser.parse_args()

    # Initialize database session and engine
    session = Session()

    # Clear tables if requested
    if args.clear_tables:
        clear_tables(args, engine)

    # Call specified functions
    if args.add_restaurant_urls:
        add_restaurant_urls(session)

    if args.add_restaurants:
        add_restaurants(session)

    if args.add_summaries:
        add_summaries(session, engine)

    # Close the session
    session.close()
    print("Database session closed. All operations completed.")

if __name__ == "__main__":
    main()