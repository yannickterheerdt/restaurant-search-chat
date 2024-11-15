from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser, StrOutputParser
import os
from config import settings
from langchain_chroma import Chroma
from typing import List, Optional
from data.scheme import Session, RestaurantSummary

# Set OpenAI API key from settings
os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY


class VectorStore:
    """
    A class to manage a vector store for storing and querying restaurant summaries.
    """

    def __init__(self) -> None:
        """
        Initializes the VectorStore by setting up the vector store and LLM based on settings.
        """
        self.vector_store = self._initialize_vector_store()
        self.llm = ChatOpenAI(
            model=settings.search.OPENAI_MODEL, 
            temperature=settings.search.OPENAI_TEMPERATUE
        )

    def _initialize_vector_store(self) -> Chroma:
        """
        Initializes the Chroma vector store with OpenAI embeddings based on settings.

        Returns:
            Chroma: The initialized Chroma vector store.
        """
        embeddings = OpenAIEmbeddings(model=settings.search.EMBED_MODEL)
        return Chroma(
            collection_name=settings.search.CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=settings.search.CHROMA_DB_PATH,
            collection_metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, texts: List[str], names: List[str]) -> None:
        """
        Adds documents to the vector store.

        Args:
            texts (List[str]): List of document texts to be added to the vector store.
            names (List[str]): List of corresponding document names.
        """
        documents = [
            Document(page_content=text, metadata={'name': name}) 
            for text, name in zip(texts, names)
        ]
        self.vector_store.add_documents(documents=documents, ids=names)

    def get_recommendations(self, query: str, filters: Optional[List[str]] = None) -> List[str]:
        """
        Retrieves top restaurant recommendations based on the given query.

        Args:
            query (str): The user query for recommendations.
            filters (Optional[List[str]]): A list of restaurant names to filter the results (optional).

        Returns:
            List[str]: List of recommended restaurant names.
        """
        filter_query = {"name": {"$in": filters}} if filters else None
        documents = self.vector_store.similarity_search(
            translate_text(query), 
            k=20, 
            filter=filter_query
        )

        summaries = [document.page_content for document in documents]
        names = [document.metadata['name'] for document in documents]

        # Format summaries for the LLM prompt
        formatted_summaries = "\n".join(
            f"Restaurant name: '{name}'\nSummary: '{summary}'\n"
            for name, summary in zip(names, summaries)
        )

        # Create and execute the prompt using the system prompt from settings
        prompt = PromptTemplate.from_template(settings.search.SYSTEM_PROMPT)
        chain = prompt | self.llm | CommaSeparatedListOutputParser()

        return chain.invoke({"query": query, "summaries": formatted_summaries})


def translate_text(text: str) -> str:
    """
    Translates a given text from Dutch to English using a language model.

    Args:
        text (str): The input text in Dutch.

    Returns:
        str: The translated text in English.
    """
    llm = ChatOpenAI(
        model=settings.search.OPENAI_MODEL, 
        temperature=settings.search.OPENAI_TEMPERATUE
    )
    prompt_template = (
        "Translate the following text from Dutch to English:\n\n"
        "Dutch: {text}\n\n"
        "English:"
    )
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": text})


def main() -> None:
    """
    Main function to initialize the vector store, retrieve restaurant data from the database,
    translate summaries, and add them to the vector store.
    """
    # Initialize the vector store
    vector_store = VectorStore()

    # Fetch restaurant summaries and names from the database
    session = Session()
    summaries = session.query(RestaurantSummary).all()
    texts = [translate_text(summary.summary) for summary in summaries]
    names = [summary.name for summary in summaries]

    # Add documents to the vector store
    vector_store.add_documents(texts=texts, names=names)
    print("Documents have been added to the vector store.")


if __name__ == "__main__":
    main()
