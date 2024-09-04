# Importaciones necesarias para el funcionamiento del código
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.chat_models.ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_elasticsearch import ElasticsearchStore

# Definición de la clase ChatPDF
class ChatPDF:
    vector_store = None
    retriever = None
    chain = None
    # https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud#finding-your-cloud-id
    ELASTIC_CLOUD_ID = "e8e5a0e7a0074391b8504e28e2e0f902:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJGYyMWZlODU3ZDU0OTRmZDRhZGE4NDA4NjNjZDg1YTY2JGM2ZTY4ZGNlYjc3MjRmMTViYzM1N2ZlZWMyYzFiOTNk" #getpass("Elastic Cloud ID: ")

    # https://www.elastic.co/search-labs/tutorials/install-elasticsearch/elastic-cloud#creating-an-api-key
    ELASTIC_API_KEY = "LUVLYnBKRUIyYWVONktWZk1tVEI6dUJBSUwxSVBSRy03OFlQdlhqSnFpdw==" #getpass("Elastic Api Key: ")
    elk_index_name = "chatbot-multi-query-demo"#"tutorial76"

    def __init__(self):
        # Inicialización del modelo de chat
        self.model = ChatOllama(model="llama3.1:latest")
        
        # Configuración del divisor de texto
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024, chunk_overlap=100)
        
        # Definición de la plantilla de prompt
        self.prompt = PromptTemplate.from_template(
            """
            You are an assistant for question-answering tasks. 
            Use the following pieces of retrieved context to answer the question. 
            If you don't know the answer, just say that you don't know. 
            Use five sentences minimum and keep the answer concise.
            Question: {question} 
            Context: {context} 
            Answer:
            """
        )

    def ingest(self, pdf_path):
        # Carga del documento PDF
        # docs = PyPDFLoader(file_path=pdf_path).load()
        # # División del documento en chunks
        # chunks = self.text_splitter.split_documents(docs)
        # # Filtrado de metadatos complejos
        # chunks = filter_complex_metadata(chunks)
        
        # Creación de embeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")

        # Creación del almacén de vectores
        # vector_store = Chroma.from_documents(
        #     documents=chunks, embedding=embeddings
        # )
        
        vector_db_store = ElasticsearchStore(
            embedding=embeddings,  # Modelo de embedding a utilizar
            index_name=self.elk_index_name,  # Nombre del índice existente
            es_cloud_id=self.ELASTIC_CLOUD_ID,  # ID de la nube de Elasticsearch
            es_api_key=self.ELASTIC_API_KEY # Clave API para autenticación
        )
        
        # Configuración del recuperador de información
        self.retriever = vector_db_store.as_retriever()

        # Configuración de la cadena de procesamiento
        self.chain = ({
            "context": self.retriever,
            "question": RunnablePassthrough()
        }
            | self.prompt
            | self.model
            | StrOutputParser()
        )

    def ask(self, query: str):
        # Método para realizar preguntas
        if not self.chain:
            return "Please ingest a PDF file first."
        return self.chain.invoke(query)

    def clear(self):
        # Método para limpiar el estado
        self.vector_store = None
        self.retriever = None
        self.chain = None
