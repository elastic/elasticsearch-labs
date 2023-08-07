# Homecraft Retail demo with Elastic ESRE and Google's GenAI

This repo shows how to leverage Elastic search capabilities (both text and vector ones) togheter with Google Cloud's GenerativeAI models and VertexAI features to create a new retail experience. With this repo you will:

- Create a python streamlit app with an intelligent search bar
- Integrate with Palm2 models and VertexAI APIs
- Configure an Elastic cluster as a private data source to build context for LLMs
- Ingest data from multiple data sources (Web Crawler, files, BigQuery)
- Use Elastic's text_embeddings and vector search for finding relevant content
- Fine-tune the text-bison@001 foundation model via VertexAI for specific tasks handling
- and more...

## Configuration steps

1. Setup your Elastic cluster with ML nodes

2. Install python on your local machine. If using Homebew on macOS simply use

```bash
brew install python@3.11  
```

3. (Optional) For better python environment management use Virtual Envs. Create a folder for your project in your favourite location, enter it and create a venv named "homecraftenv". You will then install all the libraries required only inside this venv instead of globally

```bash
python -m venv homecraftenv
```

4. (Optional) If step 3 is followed, activate your virtual env. Check here https://docs.python.org/3/tutorial/venv.html commands depending on your OS. For Unix or macOS use

```bash
source homecraftenv/bin/activate
```

5. Clone this repo in your project folder.

```bash
git clone https://github.com/valerioarvizzigno/homecraft_vertex.git
```

6. Install requirements needed to run the app from the requirements.txt file

```bash
pip install -r requirements.txt 
```

7. Install gcloud SDK. It is needed to connect to VertexAI APIs. (https://cloud.google.com/sdk/docs/install-sdk)
   Follow the instructions at the link depending on your OS. If using Homebrew on macOS you can simply install it with

 ```bash
brew install --cask google-cloud-sdk
```  

8. Init gcloud and follow the CLI instructions. You have to specify the working Google Cloud project

 ```bash
gcloud init
```  

9. Authenticate the VertexAI SDK (it has been installed with requirements.txt). More info here https://googleapis.dev/python/google-api-core/latest/auth.html

 ```bash
gcloud auth application-default login
```  

10. Load the all-distillroberta-v1 (https://huggingface.co/sentence-transformers/all-distilroberta-v1) ML model in you Elastic cluster via Eland client and start it. To run Eland client you need docker installed. An easy way to accomplish this step without python/docker installation is via Google's Cloud Shell.

 ```bash
git clone https://github.com/elastic/eland.git

cd eland/

docker build -t elastic/eland .

docker run -it --rm elastic/eland eland_import_hub_model 
--url https://<elastic_user>:<elastic_password>@<your_elastic_endpoint>:9243/ 
--hub-model-id sentence-transformers/all-distilroberta-v1 
--start
 ```

11. Index  general data from a retailer website (I used https://www.ikea.com/gb/en/) with Elastic Enterprise Search's webcrawler and give the index the "search-homecraft-ikea" name (for immediate compatibility with this repo code, otherwise change the index references in all homecraft_*.py files). For better crawling performance search the sitemap.xml file inside the robots.txt file of the target webserver, and add its path to the Site Maps tab. Set a custom ingest pipeline, named "ml-inference-title-vector", working directly at crawling time, to enrich crawled documents with dense vectors. Use the previously loaded ML model for inference on the "title" field as source, and set "title-vector" as target field for dense vectors.

12. Before launching the crawler, set mappings for the title-vector field on the index

```bash
POST search-homecraft-ikea/_mapping
{
  "properties": {
    "title-vector": {
      "type": "dense_vector",
      "dims": 768,
      "index": true,
      "similarity": "dot_product"
    }
  }
}
```

13. Start crawling.

14. Index the Home Depot products dataset (https://www.kaggle.com/datasets/thedevastator/the-home-depot-products-dataset) into elastic.

15. Create a new empty index that will host the dense vectors called "home-depot-product-catalog-vector" (for immediate compatibility with this repo code, otherwise change the index references in all homecraft_*.py files) and specify mappings.

```bash
PUT /home-depot-product-catalog-vector 

POST home-depot-product-catalog-vector/_mapping
{
  "properties": {
    "title-vector": {
      "type": "dense_vector",
      "dims": 768,
      "index": true,
      "similarity": "dot_product"
    }
  }
}
```

16. Re-index the product dataset through the same ingest pipeline previously created for the web-crawler. The new index will now have vectors embedded in documents in the title-vector field.

```bash
POST _reindex
{
  "source": {
    "index": "home-depot-product-catalog"
  },
  "dest": {
    "index": "home-depot-product-catalog-vector",
    "pipeline": "ml-inference-title-vector"
  }
}
```

17. Leverage the BigQuery to Elasticsearch Dataflow's [native integration](https://www.elastic.co/blog/ingest-data-directly-from-google-bigquery-into-elastic-using-google-dataflow) to move a [sample e-commerce dataset](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce?project=elastic-sa) into Elastic. Take a look ad tables available in this dataset withih BigQuery explorer UI. Copy the ID of the "Order_items" table and create a new Dataflow job to move data from this BQ table to an index named "bigquery-thelook-order-items". You need to create an API key on the Elastic cluster and pass it along with Elastic cluster's cloud_id, user and pass to the job config. This new index will be used for retrieving user orders.

18. Clone this repo in your project folder.

```bash
git clone https://github.com/valerioarvizzigno/homecraft_vertex.git
```

19. Set up the environment variables cloud_id, cloud_pass, cloud_user (Elastic deployment) and gcp_project_id (the GCP project you're working in)

20. Fine-tune text-bison@001 via VertexAI fine-tuning feature, using the fine-tuning/fine_tuning_dataset.jsonl file. This will instruct the model in advertizing partner network when specific questions are asked. For more information about fine-tuning look at https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#generative-ai-tune-model-python

21. Run streamlit app

 ```bash
streamlit run homecraft_home.py
```  



---USE THE HOME PAGE FOR BASE DEMO---

Try queries like: 

- "List the 3 top paint primers in the product catalog, specify also the sales price for each product and product key features. Then explain in bullet points how to use a paint primer".
You can also try asking for related urls and availability --> leveraging private product catalog + public knowledge

- "could you please list the available stores in UK" --> --> it will likely use (crawled docs)

- "Which are the ways to contact customer support in the UK? What is the webpage url for customer support?" --> it will likely use crawled docs

- Please provide the social media accounts info from the company --> it will likely use crawled docs

- Please provide the full address of the Manchester store in UK --> it will likely use crawled docs

- are you offering a free parcel delivery? --> it will likely use crawled docs

- Could you please list my past orders? Please specify price for each product --> it will search into BigQuery order dataset

- List all the items I have bought in my order history in bullet points


---FOR A DEMO OF FINE-TUNED MODEL USE "HOMECRAFT FINETUNED" WEBPAGE---

Try "Anyone available at Homecraft to assist with painting my house?".
Asking this question in the fine-tuned page should suggest to go with Homecraft's network of professionals

Asking the same to the base model will likely provide a generic or "unable to help" answer.

