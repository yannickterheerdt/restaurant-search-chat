import os
import chromadb
from typing import Optional, List, Generator, Dict, Union, Any
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent    
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.base.llms.types import ChatMessage
from data.scheme import Session, RestaurantContent
from config import settings

os.environ['OPENAI_API_KEY'] = settings.OPENAI_API_KEY

class RAG:
    """
    A Retrieval-Augmented Generation (RAG) system for answering restaurant-related
    questions using a Chroma vector store and an OpenAI-based language model.

    Attributes:
        db_path (str): Path to the Chroma database.
        collection_name (str): Name of the collection within the Chroma database.
        embed_model (OpenAIEmbedding): Model used to generate embeddings for documents.
        splitter (SentenceSplitter): Tool for splitting text into nodes.
        vector_store (Optional[ChromaVectorStore]): Vector store for storing document embeddings.
        index (Optional[VectorStoreIndex]): Index for document retrieval.
        query_engine (Optional[QueryEngineTool]): Engine for querying the vector store.
        agent (Optional[OpenAIAgent]): Language model agent used for generating responses.
    """
    
    def __init__(self) -> None:
        """
        Initializes the RAG class with configurations from settings.chat.
        """
        self.db_path: str = settings.CHAT.CHROMA_DB_PATH
        self.collection_name: str = settings.CHAT.CHROMA_COLLECTION_NAME
        self.embed_model: OpenAIEmbedding = OpenAIEmbedding(model=settings.CHAT.EMBED_MODEL)
        self.splitter: SentenceSplitter = SentenceSplitter(
            chunk_size=settings.CHAT.CHUNK_SIZE, 
            chunk_overlap=settings.CHAT.CHUNK_OVERLAP
        )
        self.vector_store: Optional[ChromaVectorStore] = None
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine: Optional[QueryEngineTool] = None
        self.agent: Optional[OpenAIAgent] = None

    def _setup_vector_store(self) -> ChromaVectorStore:
        """
        Sets up and returns the Chroma vector store. If the vector store is already
        initialized, it returns the existing instance.

        Returns:
            ChromaVectorStore: Configured Chroma vector store.
        """
        if self.vector_store is None:
            db = chromadb.PersistentClient(path=self.db_path)
            chroma_collection = db.get_or_create_collection(self.collection_name)
            self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        return self.vector_store
    
    def save_documents(self, documents: List[Document]) -> None:
        """
        Saves documents to the vector store by creating an index and storing
        document nodes with embeddings.

        Args:
            documents (List[Document]): A list of Document objects to be indexed.
        """
        self.vector_store = self._setup_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        nodes = self.splitter.get_nodes_from_documents(documents)
        self.index = VectorStoreIndex(
            nodes,
            storage_context=storage_context, 
            embed_model=self.embed_model
        )

    def load_index(self) -> None:
        """
        Loads or creates a vector store index for document retrieval. 
        Initializes the vector store if not already initialized.
        """
        if self.index is None:
            self.vector_store = self._setup_vector_store()
            
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                embed_model=self.embed_model
            )

    def load_query_engine(self, k: int = 10) -> None:
        """
        Loads or creates a query engine for querying the index. Initializes
        the index if not already initialized.

        Args:
            k (int): Number of top similar documents to retrieve.
        """
        self.load_index()
        if self.query_engine is None:
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=k, response_mode='context_only', verbose=True
            )

    def load_agent(self) -> None:
        """
        Loads or creates an OpenAIAgent for handling queries. Initializes
        the query engine if not already initialized.
        """
        self.load_query_engine()
        if self.agent is None:
            query_engine_tool = QueryEngineTool(
                query_engine=self.query_engine,
                metadata=ToolMetadata(
                    name='docs',
                    description=(
                        'Provides facts and context for any question regarding restaurant information.'
                        'Use a detailed plain text question in Dutch as input to the tool.'
                    )
                )
            )
            self.agent = OpenAIAgent.from_tools(
                [query_engine_tool],
                llm=OpenAI(settings.CHAT.OPENAI_MODEL, temperature=settings.CHAT.OPENAI_TEMPERATURE),
                system_prompt=settings.CHAT.SYSTEM_PROMPT,
                verbose=True
            )
        
    def generate_response(self, message: str, chat_history: List[ChatMessage]) -> Generator[str, None, None]:
        """
        Generates a response using the language model agent based on the provided
        message and chat history.

        Args:
            message (str): The user's message to respond to.
            chat_history (List[Dict[str, Union[str, Any]]]): A list of previous chat messages.

        Returns:
            Generator[str, None, None]: A streaming response generator from the agent.
        """
        self.load_agent()
        return self.agent.stream_chat(
            message=message, 
            chat_history=chat_history, 
            tool_choice='docs'
        ).response_gen

    
def main() -> None:
    """
    Main function to initialize the RAG system, retrieve restaurant data
    from the database, and save it into the vector store.
    """
    session = Session()
    articles = session.query(RestaurantContent).all()

    documents = [
        Document(text=article.content, metadata={'name': article.name, 'source': article.source})
        for article in articles if article.content
    ]

    rag = RAG()
    rag.save_documents(documents)
    print("Documents have been added to the vector store.")

if __name__ == "__main__":
    main()
