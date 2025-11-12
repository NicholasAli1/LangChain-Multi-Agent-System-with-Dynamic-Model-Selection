"""Vector store-based memory for long-term conversation storage and retrieval."""

import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # Fallback for older versions
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.model_factory import ModelFactory
from config.settings import DEFAULT_EMBEDDING


class VectorMemory:
    """Vector store-based memory for storing and retrieving conversation history."""
    
    def __init__(
        self,
        embedding_key: Optional[str] = None,
        persist_directory: Optional[str] = None,
        collection_name: str = "conversations"
    ):
        """
        Initialize vector memory.
        
        Args:
            embedding_key: Key for embedding model (defaults to DEFAULT_EMBEDDING)
            persist_directory: Directory to persist vector store (defaults to ./memory)
            collection_name: Name for the collection
        """
        self.embedding_key = embedding_key or DEFAULT_EMBEDDING
        self.persist_directory = persist_directory or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "memory"
        )
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.embedding = ModelFactory.get_embedding(self.embedding_key)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Load or create vector store
        self.vectorstore = self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self) -> FAISS:
        """Load existing vector store or create a new one."""
        vectorstore_path = os.path.join(
            self.persist_directory,
            f"{self.collection_name}.faiss"
        )
        
        if os.path.exists(vectorstore_path):
            try:
                return FAISS.load_local(
                    self.persist_directory,
                    self.embedding,
                    allow_dangerous_deserialization=True,
                    index_name=self.collection_name
                )
            except Exception as e:
                print(f"Warning: Could not load existing vector store: {e}")
                print("Creating new vector store...")
        
        # Create new empty vector store
        return FAISS.from_texts(
            ["Initial memory"],
            self.embedding
        )
    
    def save(self):
        """Save vector store to disk."""
        try:
            self.vectorstore.save_local(
                self.persist_directory,
                index_name=self.collection_name
            )
        except Exception as e:
            print(f"Warning: Could not save vector store: {e}")
    
    def add_conversation(
        self,
        task: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a conversation to memory.
        
        Args:
            task: The user's task/query
            response: The agent's response
            metadata: Optional metadata (e.g., model used, timestamp)
        """
        # Combine task and response
        text = f"Task: {task}\nResponse: {response}"
        
        # Create metadata
        doc_metadata = metadata or {}
        doc_metadata["type"] = "conversation"
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create documents
        documents = [
            Document(page_content=chunk, metadata=doc_metadata)
            for chunk in chunks
        ]
        
        # Add to vector store
        self.vectorstore.add_documents(documents)
        
        # Save
        self.save()
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for similar conversations.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of similar documents
        """
        try:
            if filter_dict:
                results = self.vectorstore.similarity_search_with_score(
                    query,
                    k=k,
                    filter=filter_dict
                )
                # Unpack (doc, score) tuples
                return [doc for doc, score in results]
            else:
                return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            print(f"Warning: Search failed: {e}")
            return []
    
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """
        Get relevant context from memory for a query.
        
        Args:
            query: The query to find context for
            k: Number of relevant conversations to retrieve
            
        Returns:
            Formatted context string
        """
        results = self.search(query, k=k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, doc in enumerate(results, 1):
            context_parts.append(f"Previous conversation {i}:\n{doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def clear(self):
        """Clear all memory."""
        # Create new empty vector store
        self.vectorstore = FAISS.from_texts(
            ["Initial memory"],
            self.embedding
        )
        self.save()

