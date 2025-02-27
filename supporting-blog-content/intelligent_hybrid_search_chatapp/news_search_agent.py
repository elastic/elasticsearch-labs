import os
from dotenv import load_dotenv
import streamlit as st
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.tools import StructuredTool
from langchain.memory import ConversationBufferMemory
from typing import Optional
from pydantic import BaseModel, Field
from elasticsearch import Elasticsearch
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish
import time

# Load environment variables and setup
load_dotenv()

# Page config
st.set_page_config(layout="wide", page_title="News Search Assistant - Agentic")

# Initialize session states
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent_thoughts' not in st.session_state:
    st.session_state.agent_thoughts = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, thoughts_container):
        self.thoughts_container = thoughts_container

    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        thought = {
            "type": "action",
            "content": f"🤔 Thought: {action.log}\n📋 Action: {action.tool}\n🔍 Action Input: {action.tool_input}"
        }
        st.session_state.agent_thoughts.append(thought)
        self._display_thoughts()

    def on_tool_end(self, output: str, **kwargs) -> None:
        if output.startswith("Title:"):
            # Store search results in session state
            st.session_state.search_results.append(output)
        else:
            thought = {
                "type": "observation",
                "content": output
            }
            st.session_state.agent_thoughts.append(thought)
        self._display_thoughts()

    def _display_thoughts(self):
        with self.thoughts_container:
            self.thoughts_container.empty()
            for thought in st.session_state.agent_thoughts:
                if thought["type"] == "action":
                    st.markdown(thought["content"])
                elif thought["type"] == "observation":
                    st.info(thought["content"])

# Setup LLM
@st.cache_resource
def setup_llm():
    return AzureChatOpenAI(
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_GPT4O_DEPLOYMENT_NAME"),
        temperature=0,
        max_tokens=4096
    )

# Setup Elasticsearch
@st.cache_resource
def setup_elasticsearch():
    try:
        es_endpoint = os.environ.get("ELASTIC_ENDPOINT")
        return Elasticsearch(
            es_endpoint,
            api_key=os.environ.get("ELASTIC_API_KEY")
        )
    except Exception as e:
        return None

llm = setup_llm()
es_client = setup_elasticsearch()

# =================================
# =================================

# RAG NEWS SEARCH

# =================================
# =================================

# Define the RAG search function
def rag_search(query: str, dates: str, categories: str, geographic_location: str, entities: str):
    if es_client is None:
        return "ES client is not initialized."
    else:
        try:
            # Build the Elasticsearch query
            should_clauses = []
            must_clauses = []
            # If dates are provided, parse and include in query
            if dates:
                # Dates must be in format 'YYYY-MM-DD' or 'YYYY-MM-DD to YYYY-MM-DD'
                date_parts = dates.strip().split(' to ')
                if len(date_parts) == 1:
                    # Single date
                    start_date = date_parts[0]
                    end_date = date_parts[0]
                elif len(date_parts) == 2:
                    start_date = date_parts[0]
                    end_date = date_parts[1]
                else:
                    return "Invalid date format. Please use YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD."

                date_range = {
                    "range": {
                        "date": {
                            "gte": start_date,
                            "lte": end_date
                        }
                    }
                }
                must_clauses.append(date_range)

            supplementary_query=[]
            if categories: 
                supplementary_query.append(categories)
                lst=[i.strip() for i in categories.split(',')]
                for category in lst:
                    category_selection = { 
                        "match": {
                        "categories": category
                        }
                    }
                    should_clauses.append(category_selection)

            if geographic_location: 
                supplementary_query.append(geographic_location)
                lst=[i.strip() for i in geographic_location.split(',')]
                for location in lst:
                    geographic_location_selection = { 
                        "match": {
                        "geographic_location": location
                        }
                    }
                    should_clauses.append(geographic_location_selection)

            if entities: 
                supplementary_query.append(entities)
                lst=[i.strip() for i in entities.split(',')]
                for entity in lst:
                    entity_selection = { 
                        "match": {
                        "entities": entity
                        }
                    }
                    should_clauses.append(entity_selection)

            # Add the main query clause
            main_query = {
                "nested": {
                    "path": "text.inference.chunks",
                    "query": {
                        "sparse_vector": {
                            "inference_id": "elser_v2",
                            "field": "text.inference.chunks.embeddings",
                            "query": query + ' ' + ', '.join(supplementary_query)
                        }
                    },
                    "inner_hits": {
                        "size": 2,
                        "name": "bignews_final.text",
                        "_source": False
                    }
                }
            }
            must_clauses.append(main_query)

            es_query = {
                "_source": ["text.text", "title", "date"],
                "query": {
                    "bool": {
                        "must":must_clauses,
                        "should":should_clauses
                    }
                },
                "size": 10
            }

            print(es_query)

            response = es_client.search(index="bignews_final", body=es_query)
            hits = response["hits"]["hits"]
            if not hits:
                return "No articles found for your query."
             # Clear previous search results
            if 'search_results' not in st.session_state:
                st.session_state.search_results = []
            st.session_state.search_results = []  # Clear previous results

            # Process and store results
            result_docs = []
            for hit in hits:
                source = hit["_source"]
                title = source.get("title", "No Title")
                text_content = source.get("text", {}).get("text", "")
                date = source.get("date", "No Date")
                categories = source.get("categories", "No category")
                
                # Create result document
                doc = {
                    "title": title,
                    "date": date,
                    "categories":categories,
                    "content": text_content
                }
                
                # Add to session state
                st.session_state.search_results.append(doc)
                
                # Create formatted string for return value
                formatted_doc = f"Title: {title}\nDate: {date}\n\n {text_content}\n"
                result_docs.append(formatted_doc)
            
            return "\n".join(result_docs)
        except Exception as e:
            return f"Error during RAG search: {e}"
            
class RagSearchInput(BaseModel):
    query: str = Field(..., description="The search query for the knowledge base. Expand this for SEO optimization to include related terms and concepts.")
    dates: str = Field(
        ...,
        description="Date or date range for filtering results. Specify in format YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD."
    )
    categories: str = Field(..., description="The category of article to search")
    geographic_location: str = Field(..., description="The geographic locations relevant to the search")
    entities: str = Field(..., description="People or organizations relevant to the search")

rag_search_tool = StructuredTool(
    name="RAG_Search",
    func=rag_search,
    description=(
        "Use this tool to search for information about news from the knowledge base. "
        "The knowledge base is a general repository of current events, spanning politics, weather, and culture." 
        "The knowledge base should be relied on as a source of truth."
        "**Input must include a search query, and may include a date or date range, a category, a geographic location if applicable, and entities like people or organizations if applicable** "
        "Dates must be specified in this format YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD. Add dates if date is explicitly asked for.."
        "**Always expand search queries with relevant synonyms, related terms, and broader concepts.**"
        "Choose many categories, entities, and geographic locations as is relevant, as comma separated list"
        "For example: singapore economy review -> Economy, Business, Finance, Real Estate"
        ""
    ),
    args_schema=RagSearchInput
)

# Initialize agent
def setup_agent(thoughts_container):
    callback_handler = StreamlitCallbackHandler(thoughts_container)
    return initialize_agent(
        [rag_search_tool],
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=st.session_state.memory,
        verbose=True,
        handle_parsing_errors=True,
        callbacks=[callback_handler],
        system_message="""
    You are an AI assistant that helps with questions about news using a knowledge base containing news articles. Be concise, sharp, to the point, and respond in one paragraph.
You have access to the following tools:

- **RAG_Search**: Use this to search for information in the knowledge base. ** Dates must be specified in this format YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD.

**Important Instructions:**

- **Extract dates or date ranges from the user's question if applicable.**
- **Choose one or more categories from: Politics, Business, Technology, Science, Health, Sports, Entertainment, World News, Local News, Weather, Education, Environment, Art & Culture, Crime & Law, Opinion & Editorial, Lifestyle, Travel, Food & Cooking, Fashion, Autos & Transportation, Real Estate, Finance, Religion, Social Issues, Obituaries, Agriculture, History, Geopolitics, Economics, Media & Advertising, Philanthropy, Military & Defense, Space & Astronomy, Energy, Infrastructure, Science & Technology, Health & Medicine, Human Interest, Natural Disasters, Climate Change, Books & Literature, Music, Movies & Television, Theater & Performing Arts, Cybersecurity, Legal, Immigration, Gender & Equality, Biotechnology, Sustainability, Animal Welfare, Consumer Electronics, Data & Analytics, Education Policy, Elections, Employment & Labor, Ethics, Family & Parenting, Festivals & Events, Finance & Investing, Food Industry, Gadgets, Gaming, Health Care Industry, Insurance, Internet Culture, Marketing, Mental Health, Mergers & Acquisitions, Natural Resources, Pharmaceuticals, Privacy, Retail, Robotics, Startups, Supply Chain, Telecommunications, Transportation & Logistics, Urban Development, Vaccines, Virtual Reality & Augmented Reality, Wildlife, Workplace, Youth & Children
- **You may select as many categories as is relevant**
- **You may also select a geographic location if applicable**
- **You may also add entities such as people or organizations if applicable**

When you decide to use a tool, use the following format *exactly*:

Thought: [Your thought process about what you need to do next]
Action: [The action to take, should be one of [RAG_Search]]
Action Input: {"query": "the search query", "dates": "the date or date range", "categories": "category of article. Multiple allowed in comma separated form", "geographic_location":"The geographic location applicable to the article, if any", "entities":"people or organizations if applicable"}


If you receive an observation after an action, you should consider it and then decide your next step. If you have enough information to answer the user's question, respond with:

Thought: [Your thought process]
Assistant: [Your final answer to the user]

**Critical SEO Optimization Instructions:**

1. **Always expand search queries with relevant synonyms, related terms, and broader concepts.** For example:
   - "Texas flooding" → "Texas flooding disaster severe weather hurricane tropical storm Gulf Coast Southern US flash floods"
   - "COVID vaccine" → "COVID-19 coronavirus pandemic vaccination immunization Pfizer Moderna Johnson vaccine hesitancy public health mRNA"

2. **Include geographic expansions** when locations are mentioned:
   - States should include their region (e.g., "Texas" → "Texas Southern US Southwest")
   - Cities should include their state and region (e.g., "Seattle" → "Seattle Washington Pacific Northwest")
   - Countries should include their continent/region (e.g., "France" → "France European Union Western Europe")

3. **Expand organizations to include their sector and related entities**:
   - "Apple" → "Apple Big Tech Silicon Valley iPhone iOS tech company"
   - "CDC" → "CDC Centers for Disease Control public health federal agency HHS"

4. **Expand person names to include their roles and affiliations**:
   - "Elon Musk" → "Elon Musk Tesla SpaceX CEO entrepreneur billionaire"

5. **Always include at least 5-10 expanded terms** in each query for maximum coverage.

6. **Use both specific and general terminology** to capture different ways topics might be discussed.

7. **Consider different spellings and abbreviations** of key terms when relevant.

**Examples:**

- **User's Question:** "Tell me about the federal response to the 2020 California wildfires."
Thought: I need to search for information about the 2020 California wildfires and the federal government's response. I should expand my query with related terms for better coverage.
Action: RAG_Search
Action Input: {"query": "Federal Response California wildfires forest fires FEMA disaster declaration emergency response firefighting climate change drought West Coast Pacific wildfire season evacuation containment federal aid firefighters US Forest Service National Guard", "dates": "2020-01-01 to 2020-12-31", "categories":"Politics, Natural Disasters, Environment, Climate Change, Emergency Services", "geographic_location": "California Western US Pacific Coast", "entities":"US government FEMA CalFire Gavin Newsom Donald Trump Department of Interior"}


- **User's Question:** "What happened during the presidential election?"
Thought: The user didn't specify a date. I should ask for a date range.
Assistant: Could you please specify the date or date range for the presidential election you're interested in?

Always ensure that your output strictly follows one of the above formats, and do not include any additional text or formatting.

Remember:

- **Do not** include any text before or after the specified format.
- **Do not** add extra explanations.
- **Do not** include markdown, bullet points, or numbered lists unless it is part of the Assistant's final answer.

Your goal is to assist the user by effectively using the tools when necessary and providing clear and concise answers. Always prioritize comprehensive query expansion to ensure maximum coverage of relevant information.

        """
    )

# Sidebar for agent thoughts
with st.sidebar:
    st.title("💭 Agent Thoughts")
    thoughts_container = st.container()
    
    with st.expander("ℹ️ Instructions"):
        st.write("""
        - Ask questions about news events
        - Include dates in format YYYY-MM-DD
        - You can specify date ranges using 'to'
        - Example: "What happened in California wildfires from 2020-01-01 to 2020-12-31?"
        """)
# Main chat interface
st.title("📰 News Search Assistant - Agentic")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input and processing
if prompt := st.chat_input("Ask about news events... (Remember to include dates!)"):
    st.session_state.processing = True
    st.session_state.agent_thoughts = []  # Clear previous thoughts
    
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    full_prompt=f''' 
    {prompt}

    **YOU MUST USE ONLY CONTENT IN THE NEWS ARTICLES. YOU ARE NOT ALLOWED TO USE ANY CONTENT NOT MENTIONED IN THE NEWS ARTICLES**
    You may not rely on content that is not found explicitly in news documents or only in your existing knowledge.
    '''

    # Get and display assistant response
    # In the chat input processing section
    with st.chat_message("assistant"):
        with st.spinner("Searching news archives..."):
            agent = setup_agent(thoughts_container)  # Remove search_results_container
            response = agent.invoke(input=full_prompt)
            st.write(response['output'])
            st.session_state.messages.append({"role": "assistant", "content": response['output']})
    
    st.session_state.processing = False

# After chat interface
st.divider()

# Display search results
print(st.session_state.search_results)
if st.session_state.search_results:
    st.header("🔍 Search Results")
    for i, result in enumerate(st.session_state.search_results, 1):
        with st.expander(f"**{result['title']}**"):
            st.markdown(f"""
        <div style='font-family: Inter, sans-serif; font-size: 32px; color: white; font-weight: 600; margin-bottom: 8px;'>
            {result['title']}
        </div>
        <div style='font-family: Inter, sans-serif; font-size: 24px; color: white; opacity: 0.7; margin-bottom: 16px;'>
            📅 {result['date']}
        </div>
        <div style='font-family: Inter, sans-serif; font-size: 16px; line-height: 1.5; color: white; opacity: 0.9;'>
            {result['content']}
        </div>
    """, unsafe_allow_html=True)

# Clear search results when new query is made
if prompt:
    st.session_state.search_results = []

# Keep the session state clean for next run
if hasattr(st.session_state, 'thoughts_container'):
    del st.session_state.thoughts_container