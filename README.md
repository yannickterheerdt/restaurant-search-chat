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
   git clone https://github.com/your-username/restaurant-search-chat.git
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

##  **How to Run**


## **Project Structure**

### Data management (`./data/` folder)
- `main.py`:
- `scheme.py`:
- `crud.py`:
- `parser.py`:
- `summary.py`:
- `webdriver.py`:
- `/tests/`: 

### Search Application Flask (`./apps/search/` folder)
- `app.py`:
- `vectorstore.py`:
- `templates/index.html`: 

### Chat Application Streamlit (`./apps/chat/` folder)
- `app.py`:
- `rag.py`:
