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
   ```.secrets.toml
   OPENAI_API_KEY = 'sk-...'

##  **How to Run**


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

### Search Application Flask (`./apps/search/` folder)
- `app.py`:
- `vectorstore.py`:
- `templates/index.html`: 

### Chat Application Streamlit (`./apps/chat/` folder)
- `app.py`:
- `rag.py`:
