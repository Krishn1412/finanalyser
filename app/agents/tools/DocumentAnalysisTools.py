import asyncio
import base64
import json
import os
import uuid
from io import BytesIO
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
import pypdfium2 as pdfium
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import PromptTemplate
from PyPDF2 import PdfReader
from langchain_core.output_parsers import StrOutputParser
from config import GOOGLE_API_KEY

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
MODEL = "gemini-1.5-pro"


async def parse_page_with_gemini(base64_image: str) -> str:
    """
    Extracts text from an image using Gemini Pro Vision.
    """
    model = genai.GenerativeModel(MODEL)
    image_data = base64.b64decode(base64_image)

    image_data = {
        "mime_type": "image/jpeg",
        "data": image_data
    }

    # Generate content
    response = model.generate_content(
        contents=[
            {"role": "user", "parts": [
                {"text": "Extract information from this image into text:"},
                {"inline_data": image_data}
            ]}
        ],
        stream=False
    )

    return response.text.strip() if response.text else ""

def get_pdf_text(filepath):
    text = ""
    pdf_reader = PdfReader(filepath)
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text

async def document_analysis(filename: str) -> list:
    """
    Extract text from a PDF document using Gemini.
    """
    pdf = pdfium.PdfDocument(filename)
    images = []

    for i in range(len(pdf)):
        page = pdf[i]
        image = page.render(scale=8).to_pil()
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_byte = buffered.getvalue()
        img_base64 = base64.b64encode(img_byte).decode("utf-8")
        images.append(img_base64)

    text_of_pages = await asyncio.gather(
        *[parse_page_with_gemini(image) for image in images]
    )
    return text_of_pages


def process_and_store_text(
    docs_list: list, faiss_db_path: str = "faiss_index"
) -> FAISS:
    """
    Processes extracted text, generates embeddings using Gemini, and stores them in FAISS.

    Args:
        docs_list (list): Extracted text from the document.
        faiss_db_path (str): Path to store FAISS index.

    Returns:
        FAISS retriever object.
    """
    # Save results to a temporary file
    output_file_path = f"{uuid.uuid4()}.txt"
    with open(output_file_path, "w") as json_file:
        json.dump(docs_list, json_file, indent=2)

    print(f"Data has been written to {output_file_path}")

    # Load text data
    loader = TextLoader(output_file_path)
    data = loader.load()

    # Delete the file after loading
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
        print(f"File {output_file_path} deleted successfully.")

    # Split text into chunks for embedding
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=500)
    doc_splits = text_splitter.split_documents(data)

    # Store in FAISS

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    faiss_db = FAISS.from_texts(data[0].page_content, embedding=embeddings)
    faiss_db.save_local(faiss_db_path)

    return faiss_db.as_retriever(search_type="similarity", search_kwargs={"k": 4})


def call_document_analysis(pdf_filename):
    docs_list = get_pdf_text(str(pdf_filename))
    retriever = process_and_store_text(docs_list)

    # Create retriever tool
    retriever_tool = create_retriever_tool(
        retriever,
        "document_understanding",
        "Retrieve and provide insights on document content analysis and knowledge extraction",
    )

    tools = [retriever_tool]
    return tools
