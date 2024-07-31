import os
import logging
import os
from openai import AzureOpenAI
from prompts import BASIC_RAG_PROMPT, ELASTIC_SEARCH_QUERY_GENERATOR_PROMPT, RAG_QUESTION_GENERATOR_PROMPT, HYDE_DOCUMENT_GENERATOR_PROMPT
from dotenv import load_dotenv
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY_1"),  
    api_version="2024-06-01",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
AZURE_OPENAI_DEPLOYMENT_NAME=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

class LLMProcessor:
    def __init__(self, api_key=None, model="gpt-4o"):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY_1")
        self.model = model
        self.client = AzureOpenAI(
                            api_key=self.api_key,  
                            api_version="2024-06-01",
                            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                            )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"LLMProcessor initialized with model: {self.model}")

    def _process_request(self, system_prompt, user_prompt):
        self.logger.info(f"Processing request with model: {self.model}")
        try:
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4096
            )
            self.logger.info("Request processed successfully")
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            raise

    def _execute_task(self, task_name, prompt, prompt_template):
        self.logger.info(f"Executing task: {task_name}")
        try:
            result = self._process_request(prompt_template, prompt)
            self.logger.info(f"{task_name.capitalize()} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error in {task_name}: {str(e)}")
            raise

    def generate(self, prompt):
        return self._execute_task("RAG answer generation", prompt, "")

    def generate_questions(self, document):
        return self._execute_task("Document:", document, RAG_QUESTION_GENERATOR_PROMPT)

    def basic_qa(self, context, query):
        prompt=f'''
        Context:
        {context}

        Query: 
        {query}
        '''
        return self._execute_task("RAG answer generation", prompt, BASIC_RAG_PROMPT)

    def generate_query(self, query):
        prompt=f'''
        User Question:
        {query}
        '''
        return self._execute_task("Elastic Search Query Generation", prompt, ELASTIC_SEARCH_QUERY_GENERATOR_PROMPT)
    
    def generate_HyDE(self, query):
        prompt=f'''
        User Question:
        {query}
        '''
        return self._execute_task("Elastic Search Query Generation", prompt, HYDE_DOCUMENT_GENERATOR_PROMPT)

    # def extract_entities(self, text, existing_entities=None):
    #     prompt = text
    #     if existing_entities:
    #         prompt += f"\n\nExisting entities: {existing_entities}"
    #         self.logger.info("Using existing entities in extraction")
    #     return self._execute_task("extracting entities", prompt, EXTRACT_ENTITIES_PROMPT)

    # def extract_relationships(self, text, entities):
    #     prompt = f"Text: {text}\n\nEntities: {entities}"
    #     return self._execute_task("extracting relationships", prompt, EXTRACT_RELATIONSHIPS_PROMPT)
    

