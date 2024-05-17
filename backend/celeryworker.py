
from celery import Celery
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader  # Import AzureAIDocumentIntelligenceLoader if not already imported
from langchain.docstore.document import Document
from main import process_uploaded_document


# Define Celery app
celery_app = Celery('tasks', broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/0')

# Define Celery task
@celery_app.task()
def process_uploaded_document(file_path, filename, user_id):
    try:
        # Initiate Azure AI Document Intelligence to load the document. You can either specify file_path or url_path to load the document.
        loader = AzureAIDocumentIntelligenceLoader(file_path=file_path, api_key=os.environ['AZURE_DOCUMENT_INTELLIGENCE_KEY'], api_endpoint=os.environ['AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'], api_model="prebuilt-layout")
        docs = loader.load()

        # Split the document into chunks base on markdown headers.
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        docs_string = docs[0].page_content
        splits = text_splitter.split_text(docs_string)

        # Embed the splitted documents and insert into Azure Search vector store
        index_name = filename.lower().replace('.', '-').replace('-pdf','').replace(' ','')
        print(f"index name is{index_name}")

        try:
            get_index(index_name)
        except Exception:
            index_name: str = index_name
            vector_store: AzureSearch = AzureSearch(
                azure_search_endpoint=vector_store_address,
                azure_search_key=vector_store_password,
                index_name=index_name,
                embedding_function=aoai_embeddings.embed_query,
            )    
            vector_store.add_documents(documents=splits)

        index_result = documents.find_one({"index_name": index_name, "id": user_id})


        if index_result is None:
            documents.insert_one({"id": user_id, "index_name": index_name, "filename": filename})

    except Exception as e:
        raise e
