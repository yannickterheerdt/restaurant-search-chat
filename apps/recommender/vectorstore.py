from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser, StrOutputParser
import os
from config import settings
from langchain_chroma import Chroma
import argparse
from data.scheme import Session, RestaurantSummary

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY

class VectorStore:
    def __init__(self):
        self.vector_store = self._initialize_vector_store()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def _initialize_vector_store(self):
        """Initializes the Chroma vector store with embeddings."""
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        return Chroma(
            collection_name="restaurant_summaries",
            embedding_function=embeddings,
            persist_directory="./chroma",
            collection_metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, texts, names):
        """Adds a list of document texts with corresponding names to the vector store."""
        documents = [Document(page_content=text, metadata={'name': name}) for text, name in zip(texts, names)]
        self.vector_store.add_documents(documents=documents, ids=names)

    def get_recommendations(self, query, filters):
        """Returns top recommended restaurant names based on the input query."""
        filter = {"name": {"$in": filters}} if filters else None
        documents = self.vector_store.similarity_search(translate_text(query), k=20, filter=filter)

        summaries = [document.page_content for document in documents]
        names = [document.metadata['name'] for document in documents]

        formatted_summaries = "\n".join(
            f"Restaurant name: '{name}'\nSummary: '{summary}'\n" for name, summary in zip(names, summaries)
        )

        prompt = PromptTemplate.from_template(settings.PROMPT_SUMMARY_RELEVANCE)

        chain = prompt | self.llm | CommaSeparatedListOutputParser()

        return chain.invoke({"query": query, "summaries": formatted_summaries})

def translate_text(text: str) -> str:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt_template = (
            "Translate the following text from Dutch to English:\n\n"
            "Dutch: {text}\n\n"
            "English:"
    )
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": text})

def main():
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