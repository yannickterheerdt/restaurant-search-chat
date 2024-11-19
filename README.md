# **Restaurant Search and Chat**

A hobby project that integrates web scraping, a search engine, and an interactive chat interface to explore restaurants in Rotterdam.

## **Features**

- **Web Scraping with Selenium:** Extract restaurant data and related articles from dynamic web pages using automated browser interactions.
- **SQLite Database with SQLAlchemy:** Store and manage scraped data efficiently in a lightweight relational database.
- **Flask-based Restaurant Search Engine:**
  - Search for restaurants based on their summaries using OpenAI vector embeddings stored in a Chroma vector database.
  - Apply filters to refine results by attributes such as meal type, price level, and district.
- **Streamlit-based Chat Interface:** 
  - Interact with scraped articles through a simple chatbot interface built with Streamlit.
  - Conversations are powered by an OpenAI Agent integrated with a Chroma vector database, created using LlamaIndex.
 
## **Installation**

Follow these steps to set up and run the project locally:

### **Prerequisites**
- Ensure you have **Python 3.8** or later installed on your system.
- Install **Git** for cloning the repository.
- Obtain an **OpenAI API key** from [OpenAI](https://platform.openai.com/signup/).

### **Steps**

1. **Clone the Repository**  
   Clone the repository to your local machine using Git:
   ```bash
   git clone https://github.com/yannickterheerdt/restaurant-search-chat.git
   cd restaurant-search-chat
2. **Create a Virtual Environment**
   Set up a virtual environment to isolate project dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
3. **Install Dependencies**
   Install the required packages using `pip`:
   ```bash
   pip install -r requirements.txt
4. **Open AI API Key**
   Add your Open AI API Key to a file called `.secrets.toml` in the main project directory. The name of the variable should be `OPENAI_API_KEY`:
   ```secrets.toml
   OPENAI_API_KEY = 'sk-...'
5. **Download ChromeDriver**
   Download the current ChromeDriver version from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/). Put the downloaded `chromedriver.exe` file in a folder called `chromedriver` in the main project directory.

##  **How to Run**

## **Data Management**

To manage restaurant data, use the following script:

```bash
python -m data.main
```

### **Available Parameters**
- `--add_restaurant_urls`  
  Scrapes restaurant URLs and saves them to the database.

- `--add_restaurant`  
  For each restaurant URL, scrapes detailed restaurant information and related articles.

- `--add_summaries`  
  Generates summaries for each restaurant using the scraped information and articles.

- `--clear_tables`  
  Clears the tables specified by the provided `--add_..` parameters.

**Note**: Each operation is executed only for restaurants that are not already in the database.

## **Search Application**

To enable restaurant search functionality:

1. **Add Articles to the Vector Database**  
   Run the following command to index articles for vector-based search:
   ```bash
   python -m apps.search.vectorstore
   ```

2. **Start the Flask Search Application**  
   Launch the search app with:
   ```bash
   python -m apps.search.app
   ```

## **Chat Application**

To enable chat functionality:

1. **Add Articles to the Vector Database**  
   Similar to the search application, index articles with:
   ```bash
   python -m apps.chat.rag
   ```

2. **Start the Streamlit Chat Application**  
   Run the Streamlit-based chat app using:
   ```bash
   streamlit run apps/chat/app.py
   ```


## **Project Structure**

### Data management (`./data/` folder)
- `main.py`: The main file for scraping restaurant URLs, information, and articles. It also creates summaries using the OpenAI API.
- `crud.py`: Provides functions to interact with the SQLite database using SQLAlchemy, including storing and querying database objects.
- `scheme.py`:  Defines SQLAlchemy tables:
   - `RestaurantUrl`: Stores restaurant URLs.
   - `RestaurantData`: Stores general restaurant information.
   - `RestaurantContent`: Stores articles related to the restaurants.
   - `RestaurantSummary`: Stores summaries generated for each restaurant.
- `parser.py`: Contains multiple classes for parsing web-scraped HTML using the Python package `Parsel`, tailored for different webpage structures.
- `summary.py`: Includes functions to generate summaries for restaurants based on article text and information, leveraging the OpenAI API.
- `webdriver.py`: Handles the web scraping logic using Selenium in combination with ChromeDriver.
- `/tests/`: Contains simple integration tests for web scraping restaurant data and saving it to the database.

### **Search Application Flask** (`./apps/search/` folder)

- **`app.py`**: A Flask application with three routes:
  1. **`/get_filtered_names`** `[POST]`: Returns the names of restaurants that match the provided filters.
  2. **`/get_filtered_options`** `[GET]`: Queries the unique filter options available in the database.
  3. **`/query`** `[POST]`: Retrieves recommended restaurants based on a query and returns their details.

- **`vectorstore.py`**: Manages the Chroma vector database using Langchain and OpenAI. Can be run directly to initialize the vector store with all documents.

- **`templates/index.html`**: The HTML template for the Flask application. Filters and restaurant cards are dynamically rendered via JavaScript.

- **`static/scripts.js`**: Contains JavaScript code for dynamic interaction within the Flask application.

- **`static/style.css`**: Defines the CSS styles for the Flask application.


### **Chat Application Streamlit** (`./apps/chat/` folder)

- **`app.py`**: A Streamlit application that provides a simple chat interface for interacting with the articles.

- **`rag.py`**: Implements a query and retrieval system using LlamaIndex and OpenAI. Can be run directly to initialize the vector store with all documents.

