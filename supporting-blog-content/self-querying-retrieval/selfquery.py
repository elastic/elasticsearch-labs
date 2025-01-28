from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_elasticsearch import ElasticsearchStore
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.docstore.document import Document
import os

# --- Environment Configuration (Set these variables) ---
os.environ["AZURE_OPENAI_API_KEY"] = ""  # Replace with your actual key
os.environ["AZURE_ENDPOINT"] = ""  # Replace with your endpoint
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4"  # For LLM
os.environ["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME"] = "text-embedding-ada-002"  # For embeddings

ELASTIC_CLOUD_ID = "" #if using Elastic Cloud, your Cloud ID
ELASTIC_USERNAME = "" # ES user, alternatively can be API key
ELASTIC_PASSWORD = ""
ELASTIC_INDEX_NAME = "yourElasticIndex" #replace with your index name, if no matching index is present one will be created

# --- Initialize LLM and Embeddings ---
llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_ENDPOINT"],
    deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    model_name="gpt-4",
    api_version="2024-02-15-preview"
)

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_ENDPOINT"],
    model="text-embedding-ada-002"
)

# --- Define Metadata Attributes ---
metadata_field_info = [
    AttributeInfo(
        name="year",
        description="The year the movie was released",
        type="integer",
    ),
    AttributeInfo(
        name="rating",
        description="The rating of the movie (out of 10)",
        type="float",
    ),
    AttributeInfo(
        name="genre",
        description="The genre of the movie",
        type="string",
    ),
    AttributeInfo(
        name="director",
        description="The director of the movie",
        type="string",
    ),
    AttributeInfo(
        name="title",
        description="The title of the movie",
        type="string",
    )
]

# --- Ingest the Documents ---
docs = [
 Document(
        page_content="A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        metadata={"year": 2010, "rating": 8.8, "genre": "science fiction", "title": "Inception"},
    ),
    Document(
        page_content="When the menace known as the Joker emerges from the shadows, it causes Batman to question everything he stands for.",
        metadata={"year": 2008, "rating": 9.0, "genre": "action", "title": "The Dark Knight"},
    ),
    Document(
        page_content="The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        metadata={"year": 1972, "rating": 9.2, "genre": "crime", "title": "The Godfather"},
    ),
    Document(
        page_content="A young hobbit, Frodo, is tasked with destroying an ancient ring that holds the power to enslave the world.",
        metadata={"year": 2001, "rating": 8.8, "genre": "fantasy", "title": "The Lord of the Rings: The Fellowship of the Ring"},
    ),
    Document(
        page_content="A cyborg assassin travels back in time to kill the mother of the future leader of the human resistance.",
        metadata={"year": 1984, "rating": 8.0, "genre": "science fiction", "title": "The Terminator"},
    ),
    Document(
        page_content="A cowboy doll is profoundly threatened when a new spaceman action figure replaces him as the top toy in a boy's room.",
        metadata={"year": 1995, "rating": 8.3, "genre": "animation", "title": "Toy Story"},
    ),
    Document(
        page_content="A young wizard, Harry Potter, begins his journey at Hogwarts School of Witchcraft and Wizardry, where he learns of his magical heritage.",
        metadata={"year": 2001, "rating": 7.6, "genre": "fantasy", "title": "Harry Potter and the Sorcerer's Stone"},
    ),
    Document(
        page_content="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        metadata={"year": 2014, "rating": 8.6, "genre": "science fiction", "title": "Interstellar"},
    ),
    Document(
        page_content="A former Roman General seeks revenge against the corrupt emperor who murdered his family and sent him into slavery.",
        metadata={"year": 2000, "rating": 8.5, "genre": "action", "title": "Gladiator"},
    ),
    Document(
        page_content="A young lion prince is exiled from his kingdom and must learn the true meaning of responsibility and bravery.",
        metadata={"year": 1994, "rating": 8.5, "genre": "animation", "title": "The Lion King"},
    ),
]

# Generate embeddings *before* creating the ElasticsearchStore
texts = [doc.page_content for doc in docs]
metadatas = [doc.metadata for doc in docs]
doc_embeddings = embeddings.embed_documents(texts)

es_store = ElasticsearchStore(
    es_cloud_id=ELASTIC_CLOUD_ID,
    es_user=ELASTIC_USERNAME,
    es_password=ELASTIC_PASSWORD,
    index_name=ELASTIC_INDEX_NAME,
    embedding=embeddings, 
)

es_store.add_embeddings(text_embeddings=list(zip(texts, doc_embeddings)), metadatas=metadatas)



# --- Create the Self-Query Retriever (Using LLM) ---
retriever = SelfQueryRetriever.from_llm(
    llm,
    es_store,
    "Search for movies",
    metadata_field_info,
    verbose=True,
)

while True:
    # Prompt the user for a query
    query = input("\nEnter your search query (or type 'exit' to quit): ")
    
    # Exit the loop if the user types 'exit'
    if query.lower() == 'exit':
        break
    
    # Execute the query and print the results
    print(f"\nQuery: {query}")
    docs = retriever.invoke(query)
    print(f"Found {len(docs)} documents:")
    for doc in docs:
        print(doc.page_content)
        print(doc.metadata)
        print("-" * 20)
