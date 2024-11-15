from flask import Flask, render_template, request, jsonify
from apps.search.vectorstore import VectorStore
from data.scheme import Session, RestaurantData
from data.crud import get_complete_restaurant_data, get_unique_filter_values
from sqlalchemy.orm import Query
from sqlalchemy import or_
from typing import List, Dict, Any

app = Flask(__name__)

# Initialize the vector store
vector_store = VectorStore()

def apply_filters(query: Query, filters: List[str], field: str) -> Query:
    """
    Apply substring filters to a SQLAlchemy query for a specified field.

    Args:
        query (Query): The current SQLAlchemy query.
        filters (List[str]): List of filter strings to apply.
        field (str): The name of the field to filter.

    Returns:
        Query: The updated query with applied filters.
    """
    if filters:
        query = query.filter(or_(*[getattr(RestaurantData, field).contains(f) for f in filters]))
    return query

@app.route("/")
def index() -> str:
    """
    Render the main index page.

    Returns:
        str: The rendered HTML template for the index page.
    """
    return render_template("index.html")

@app.route('/get_filtered_names', methods=['POST'])
def get_filtered_names() -> Dict[str, Any]:
    """
    Retrieve names of restaurants matching filter criteria with substring matching.

    Returns:
        Dict[str, Any]: JSON response containing a list of matching restaurant names.
    """
    session = Session()
    try:
        # Parse filters from JSON payload
        payload = request.json or {}
        meal_types = payload.get('meal_type', [])
        districts = payload.get('district', [])
        restaurant_types = payload.get('restaurant_type', [])
        price_levels = payload.get('price_level', [])

        # Build query with reusable helper
        query = session.query(RestaurantData.name)
        query = apply_filters(query, meal_types, 'meal_type')
        query = apply_filters(query, districts, 'district')
        query = apply_filters(query, restaurant_types, 'restaurant_type')
        query = apply_filters(query, price_levels, 'price_level')

        # Retrieve distinct restaurant names
        names = [row[0] for row in query.distinct().all()]
    finally:
        session.close()

    return jsonify(names=names)

@app.route('/get_filter_options', methods=['GET'])
def get_filter_options() -> Dict[str, Any]:
    """
    Retrieve unique filter options for restaurant attributes.

    Returns:
        Dict[str, Any]: JSON response containing filter options for each feature.
    """
    session = Session()
    try:
        features = ['meal_type', 'district', 'restaurant_type', 'price_level']
        filter_options = get_unique_filter_values(session, features)
    finally:
        # Close the session after the query is done
        session.close()

    return jsonify(filter_options)

@app.route("/query", methods=["POST"])
def query() -> Dict[str, Any]:
    """
    Retrieve detailed restaurant data based on user query and filters.

    Returns:
        Dict[str, Any]: JSON response containing detailed restaurant data.
    """
    filters = request.json.get('names', [])
    question = request.json.get('question', '')

    # Get recommended restaurant names
    names = vector_store.get_recommendations(question, filters)

    session = Session()
    try:
        # Fetch complete restaurant data
        data = get_complete_restaurant_data(session, names)
    finally:
        session.close()

    return jsonify(data)

if __name__ == "__main__":
    # Run the Flask application in debug mode for development purposes
    app.run(debug=True)
