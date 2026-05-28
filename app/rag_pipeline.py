from config import *
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain
import os
from pathlib import Path

class RAGChatbot:
    def __init__(self):
        #Text to vector
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

        #AI model
        self.llm = Ollama(model=AI_MODEL, temperature=0.7)

        #Vector database
        self.vectorstore= None

        #hybrid
        self.hybrid_retriever=None

        #Setup Memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def ingest_documents(self):
        #Loads documents, splits them into chunks, and creates vector embeddings
        print("Processing documents...")

        data_path=Path("data")
        files=list(data_path.glob("**/*"))

        if not files:
            print("No files Found")
            return False

        # Create the chunk-splitter tool (ONCE!)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        #  Create empty database (ONCE!)
        self.vectorstore = Chroma(
            embedding_function=self.embeddings,
            persist_directory=VECTOR_DB_PATH
        )

        total_chunks=0

        for file in files:
            if file.suffix==".pdf":
                loader= PyPDFLoader(str(file))
            elif file.suffix==".txt":
                loader= TextLoader(str(file))
            else:
                continue
        
            for page in loader.lazy_load():
                chunks=text_splitter.split_documents([page])
            
                if chunks:
                    self.vectorstore.add_documents(chunks)
                    total_chunks+=len(chunks)
        
        print(f"Total chunks: {total_chunks}")
        self.build_hybrid_retriever()
        return True
        


       
    def load_vector_store(self):
        """Load existing vector database from disk"""
        try:
            self.vectorstore= Chroma(embedding_function=self.embeddings,persist_directory=VECTOR_DB_PATH)
            print("✅ Vector store loaded!")
            self.hybrid_retriever=self.build_hybrid_retriever()
            print("Hybrid retriever ready!")
            return True
 
        
        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            return False
        
        

    def build_hybrid_retriever(self):
        if self.vectorstore is None:
            return None
        hybriddata=self.vectorstore.get()
        raw_docs = hybriddata.get("documents")
        raw_metadatas = hybriddata.get("metadatas")
        documents=[
            Document(page_content=docs, metadata=meta) for docs,meta in zip(raw_docs,raw_metadatas)
            ]

        bm25=BM25Retriever.from_documents(documents)
        bm25.k=NUM_SEARCH_RESULTS 

        vector= self.vectorstore.as_retriever(k=NUM_SEARCH_RESULTS)

        hybrid=EnsembleRetriever(retrievers=[bm25,vector],weights=[0.5,0.5])

        return hybrid

        
    def query(self, question:str):
        "Answer a question using RAG system"

        if self.vectorstore is None:
                return {"answer": "Error: Please load documents using ingest_documents()",
                        "sources": []}
                        
        
        qa_chain= RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.hybrid_retriever,
            return_source_documents=True
        )

        result = qa_chain({"query": question})
        answer = result["result"]
        sources = []

        for doc in result["source_documents"]:
            source_info={"source" : doc.metadata.get("source","Unknown"),
                         "page": str(doc.metadata.get("page","N/A")),
                         "preview": doc.page_content[:200]

            }
            sources.append(source_info)

        return {"answer":answer,
        "sources":sources}

    def query_with_history(self, question: str):

        if self.vectorstore is None:
            return {"answer": "Error: Please load documents using ingest_documents()"}

        
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.hybrid_retriever,
            memory=self.memory
        )
        question_with_instruction = f"{question} (Please respond in English only)"

        result = qa_chain({"question": question_with_instruction})
        answer=result['answer'] 

        return {"answer":answer}

    def clear_history(self):
    
        self.memory.clear()
                   




