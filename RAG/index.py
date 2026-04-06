from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader # Now we can instantiate our model object and load documents
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore

# Loading Environment Variable as per required
load_dotenv()

# __file__ refers to the current script path
# .parent gets the directory containing the script
# / operator joins the directory with the filename

pdf_path = Path(__file__).parent / "Foundations-of-Machine-Learning-Mehryar-Mohri-Afshin-Rostamizadeh-Ameet-Talwalkar.pdf"


# Load this file in python program

loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()

# print(docs[0],docs[1],docs[2])

# Split the docs into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 400
)


chunks = text_splitter.split_documents(documents=docs)


# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model = "text-embedding-3-large"
)

vectore_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding= embedding_model,
    url="http://localhost:6333",
    collection_name= "Learning_RAG",
    force_recreate=True  # This wipes the old data and starts fresh
)


print("Congratulations!!!   Indexing of Documents done....")