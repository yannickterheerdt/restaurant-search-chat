from flask import Flask, render_template, request, jsonify
from apps.recommender.vectorstore import VectorStore
from data.scheme import Session, RestaurantData
from data.crud import get_complete_restaurant_data, get_unique_filter_values
from sqlalchemy import or_

app = Flask(__name__)

vector_store = VectorStore()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/get_filtered_names', methods=['POST'])
def get_filtered_names():
    """Retrieve names of restaurants matching filter criteria with substring matching."""
    session = Session()
    try:
        # Get filters from the JSON payload
        meal_types = request.json.get('meal_type', [])
        districts = request.json.get('district', [])
        restaurant_types = request.json.get('restaurant_type', [])
        price_levels = request.json.get('price_level', [])
        print(restaurant_types)

        # Build the query with filters using `contains` for partial matching
        query = session.query(RestaurantData.name)

        # Apply substring filtering with `contains` and `or_`
        if meal_types:
            query = query.filter(or_(*[RestaurantData.meal_type.contains(mt) for mt in meal_types]))
        if districts:
            query = query.filter(or_(*[RestaurantData.district.contains(d) for d in districts]))
        if restaurant_types:
            query = query.filter(or_(*[RestaurantData.restaurant_type.contains(rt) for rt in restaurant_types]))
        if price_levels:
            query = query.filter(or_(*[RestaurantData.price_level.contains(pl) for pl in price_levels]))

        # Retrieve and return unique names that match the filters
        names = [row[0] for row in query.distinct().all()]
        print(names)
    finally:
        session.close()

    return jsonify(names=names)

@app.route('/get_filter_options', methods=['GET'])
def get_filter_options():
    session = Session()
    try:
        features = ['meal_type', 'district', 'restaurant_type', 'price_level']
        filter_options = get_unique_filter_values(session, features)
    finally:
        # Close the session after the query is done
        session.close()

    return jsonify(filter_options)

@app.route("/query", methods=["POST"])
def query():
    filters = request.json.get('names', [])
    question = request.json.get('question', '')
    names = vector_store.get_recommendations(question, filters)

    session = Session()
    try: 
        data = get_complete_restaurant_data(session, names)
    finally:
        session.close()

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)