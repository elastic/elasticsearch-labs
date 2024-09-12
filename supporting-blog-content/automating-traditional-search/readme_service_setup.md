## Elastic Cloud 

1. Visit https://cloud.elastic.co/login?redirectTo=%2Fhome and create an account or login
2. Click on ```Create Deployment``` and deploy an Elastic cluster 
3. Click on the deployment and click on ```Copy endpoint``` next to Elasticsearch. Add this to your ```.env``` as ```ELASTIC_ENDPOINT```
4. Open Kibana and navigate to Stack Management -> Security -> API Keys
5. Click on Create API Key, copy it, and add it to your ```.env``` as ```ELASTIC_API_KEY```

## Azure OpenAI 

Refer to Microsoft documentation:
https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?tabs=command-line%2Cpython-new&pivots=programming-language-python#prerequisites