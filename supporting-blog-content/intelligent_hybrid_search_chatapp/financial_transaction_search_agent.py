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
from datetime import datetime, timedelta

# Load environment variables and setup
load_dotenv()

# Page config
st.set_page_config(layout="wide", page_title="News Search Assistant")

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
        # Check if this is a financial transaction search result set
        if "Transaction ID:" in output and "Payer:" in output:
            # Process financial transaction search results
            thought = {
                "type": "observation",
                "content": "Found transaction data:"
            }
            st.session_state.agent_thoughts.append(thought)
            
            # Extract and display summary if present
            summary = ""
            if "\nSummary:" in output:
                parts = output.split("\nSummary:", 1)
                output = parts[0]
                summary = "Summary: " + parts[1]
            
            # Check if we have results in the session state
            if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
                thought = {
                    "type": "data_display",
                    "content": st.session_state.search_results,
                    "summary": summary
                }
                st.session_state.agent_thoughts.append(thought)
            else:
                # Fallback if session state doesn't have search results
                thought = {
                    "type": "observation",
                    "content": output
                }
                st.session_state.agent_thoughts.append(thought)
        else:
            # Handle other outputs normally
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

# Financial Transactions SEARCH

# =================================
# =================================

def financial_transaction_search(query: str, 
                                date_range: str, 
                                amount_range: str,
                                payer: str,
                                payer_id: str,
                                payer_type: str,
                                payee: str,
                                payee_id: str,
                                payee_type: str,
                                payer_industry: str,
                                payee_industry: str,
                                payer_scale: str):
    if es_client is None:
        return "ES client is not initialized."
    else:
        try:
            # Build the Elasticsearch query
            must_clauses = []
            should_clauses=[]
            
            # If date range is provided, parse and include in query
            if date_range:
                # Date range must be in format 'YYYY-MM-DD' or 'YYYY-MM-DD to YYYY-MM-DD'
                date_parts = date_range.strip().split(' to ')
                if len(date_parts) == 1:
                    # Single date
                    start_date = date_parts[0]
                    end_date = date_parts[0]
                elif len(date_parts) == 2:
                    start_date = date_parts[0]
                    end_date = date_parts[1]
                else:
                    return "Invalid date format. Please use YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD."
                
                # Convert to timestamp format expected by data
                try:
                    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                    end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
                    start_timestamp = start_datetime.strftime("%Y-%m-%dT00:00:00.000Z")
                    end_timestamp = end_datetime.strftime("%Y-%m-%dT23:59:59.999Z")
                    
                    date_range_query = {
                        "range": {
                            "timestamp": {
                                "gte": start_timestamp,
                                "lte": end_timestamp
                            }
                        }
                    }
                    must_clauses.append(date_range_query)
                except ValueError:
                    return "Invalid date format. Dates must be in YYYY-MM-DD format."
            
            # # If amount range is provided, parse and include in query
            # if amount_range:
            #     amount_parts = amount_range.strip().split(' to ')
            #     if len(amount_parts) == 1:
            #         try:
            #             # Single amount - exact match
            #             exact_amount = float(amount_parts[0])
            #             amount_query = {
            #                 "match": {
            #                     "amount": exact_amount
            #                 }
            #             }
            #             should_clauses.append(amount_query)
            #         except ValueError:
            #             return "Invalid amount format. Please use a number or range like '10 to 100'."
            #     elif len(amount_parts) == 2:
            #         try:
            #             # Amount range
            #             min_amount = float(amount_parts[0])
            #             max_amount = float(amount_parts[1])
            #             amount_range_query = {
            #                 "range": {
            #                     "amount": {
            #                         "gte": min_amount,
            #                         "lte": max_amount
            #                     }
            #                 }
            #             }
            #             should_clauses.append(amount_range_query)
            #         except ValueError:
            #             return "Invalid amount range. Please use format like '10 to 100'."
            #     else:
            #         return "Invalid amount format. Please use a number or range like '10 to 100'."
            
            # Include payer type if provided
            if payer:
                payer_query = {
                    "match": {
                        "payer": payer
                    }
                }
                must_clauses.append(payer_query)

            # # Include payer type if provided
            # if payer_id:
            #     payer_id_query = {
            #         "match": {
            #             "payer_id": payer_id
            #         }
            #     }
            #     should_clauses.append(payer_id_query)

                
            # # Include payer type if provided
            # if payer_type:
            #     payer_type_query = {
            #         "match": {
            #             "payer_type": payer_type
            #         }
            #     }
            #     should_clauses.append(payer_type_query)
            
            # # Include payer type if provided
            # if payee:
            #     payee_query = {
            #         "match": {
            #             "payer_type": payee
            #         }
            #     }
            #     should_clauses.append(payee_query)

            # # Include payer type if provided
            # if payee_id:
            #     payee_id_query = {
            #         "match": {
            #             "payee_id": payee_id
            #         }
            #     }
            #     should_clauses.append(payee_id_query)

            # # Include payee type if provided
            # if payee_type:
            #     payee_type_query = {
            #         "match": {
            #             "payee_type": payee_type
            #         }
            #     }
            #     should_clauses.append(payee_type_query)
            
            # # Include payer industry if provided
            # if payer_industry:
            #     payer_industry_query = {
            #         "match": {
            #             "payer_industry": payer_industry
            #         }
            #     }
            #     should_clauses.append(payer_industry_query)
            
            # # Include payee industry if provided
            # if payee_industry:
            #     payee_industry_query = {
            #         "match": {
            #             "payee_industry": payee_industry
            #         }
            #     }
            #     should_clauses.append(payee_industry_query)
            
            # # Include payer scale if provided
            # if payer_scale:
            #     payer_scale_query = {
            #         "match": {
            #             "payer_scale": payer_scale
            #         }
            #     }
            #     should_clauses.append(payer_scale_query)
            
            # # Include general query if provided
            # if query:
            #     general_query = {
            #         "multi_match": {
            #             "query": query,
            #             "fields": ["payer", "payee", "payer_id", "payee_id"]
            #         }
            #     }
            #     should_clauses.append(general_query)
            
            # Build the final query
            es_query = {
                "_source": ["transaction_id", "payer", "payer_id", "payer_type", 
                           "payer_industry", "payer_scale", "payee", "payee_id", 
                           "payee_type", "payee_industry", "amount", "timestamp"],
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "should": should_clauses,
                    }
                },
                "size": 20,
                "sort": [
                    {"timestamp": {"order": "desc"}}
                ]
            }
            
            # Execute the search
            response = es_client.search(index="financial_transactions", body=es_query)
            hits = response["hits"]["hits"]
            
            if not hits:
                return "No transactions found matching your criteria."
                
            # Clear previous search results
            if 'search_results' not in st.session_state:
                st.session_state.search_results = []
            st.session_state.search_results = []  # Clear previous results
            
            # Process and store results
            result_docs = []
            for hit in hits:
                source = hit["_source"]
                transaction_id = source.get("transaction_id", "No ID")
                payer = source.get("payer", "Unknown")
                payer_id = source.get("payer_id", "Unknown")
                payee = source.get("payee", "Unknown")
                payee_id = source.get("payee_id", "Unknown")
                amount = source.get("amount", 0.0)
                timestamp = source.get("timestamp", "No Date")
                payer_type = source.get("payer_type", "Unknown")
                payee_type = source.get("payee_type", "Unknown")
                payer_industry = source.get("payer_industry", "None")
                payee_industry = source.get("payee_industry", "None")
                payer_scale = source.get("payer_scale", "Unknown")
                
                # Format date for display
                try:
                    date_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.000Z")
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_date = timestamp
                
                # Create result document
                doc = {
                    "transaction_id": transaction_id,
                    "payer": payer,
                    "payer_id": payer_id,
                    "payer_type": payer_type,
                    "payer_industry": payer_industry,
                    "payer_scale": payer_scale,
                    "payee": payee,
                    "payee_id": payee_id,
                    "payee_type": payee_type,
                    "payee_industry": payee_industry,
                    "amount": f"${amount:.2f}",
                    "timestamp": formatted_date
                }
                
                # Add to session state
                st.session_state.search_results.append(doc)
                
                # Create formatted string for return value
                formatted_doc = (f"Transaction ID: {transaction_id}\n"
                                f"Date: {formatted_date}\n"
                                f"Amount: ${amount:.2f}\n"
                                f"Payer: {payer} ({payer_id}, {payer_type}, {payer_industry})\n"
                                f"Payee: {payee} ({payee_id}, {payee_type}, {payee_industry})\n")
                result_docs.append(formatted_doc)
            
            # Add summary statistics
            total_amount = sum(float(doc["amount"].replace('$', '')) for doc in st.session_state.search_results)
            transaction_count = len(st.session_state.search_results)
            summary = f"\nSummary: Found {transaction_count} transactions totaling ${total_amount:.2f}"
            
            return "\n\n".join(result_docs) + summary
            
        except Exception as e:
            return f"Error during financial transaction search: {e}"
            
class FinancialTransactionSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Optional general search query (searches across entity names and IDs)."
    )
    date_range: str = Field(
        ...,
        description="Date or date range for filtering transactions. Specify in format YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD."
    )
    amount_range: str = Field(
        ...,
        description="Amount or amount range for filtering transactions. Specify as a number (e.g., '100') or range (e.g., '10 to 1000')."
    )
    payer: str = Field(
        ...,
        description="Filter by payer's name (eg. Poklat Communications)."
    )
    payer_id: str = Field(
        ...,
        description="Filter by payer ID (e.g. B178282G)."
    )
    payer_type: str = Field(
        ...,
        description="Filter by payer type (e.g., 'retail' or 'business')."
    )
    payee: str = Field(
        ...,
        description="Filter by payee's name (eg. Crisco Smalls)."
    )
    payee_id: str = Field(
        ...,
        description="Filter by payee's ID (e.g. S9210200I)."
    )
    payee_type: str = Field(
        ...,
        description="Filter by payee type (e.g., 'retail' or 'business')."
    )
    payer_industry: str = Field(
        ...,
        description="Filter by payer industry (e.g., 'Manufacturing', 'Financial Services', 'Energy', etc.)."
    )
    payee_industry: str = Field(
        ...,
        description="Filter by payee industry (e.g., 'Manufacturing', 'Financial Services', 'Energy', etc.)."
    )
    payer_scale: str = Field(
        ...,
        description="Filter by payer's typical transaction scale (micro, small, medium, large, xlarge)."
    )

financial_transaction_search_tool = StructuredTool(
    name="Financial_Transaction_Search",
    func=financial_transaction_search,
    description=(
        "Use this tool to search for and analyze financial transactions from the database. "
        "The database contains transaction records with details about payers, payees, amounts, and timestamps. "
        "**Input can include any combination of: general query, date range, amount range, payer/payee names, payer/payee ids, payer/payee types, "
        "payer/payee industries, and payer transaction scale.** "
        "\n\nKey search capabilities:"
        "\n- Date filtering (YYYY-MM-DD or YYYY-MM-DD to YYYY-MM-DD)"
        "\n- Amount filtering (single value or range like '10 to 1000')"
        "\n- Entity type filtering (retail or business)"
        "\n- Industry filtering (e.g., Manufacturing, Financial Services)"
        "\n- Transaction scale filtering (micro, small, medium, large, xlarge)"
        "\n\nExample: To find all large business-to-business transactions in the manufacturing industry from January 2023, "
        "use date_range='2023-01-01 to 2023-01-31', payer_type='business', payee_type='business', "
        "payer_industry='Manufacturing', payer_scale='large'"
    ),
    args_schema=FinancialTransactionSearchInput
)
# Initialize agent
def setup_agent(thoughts_container):
    callback_handler = StreamlitCallbackHandler(thoughts_container)
    return initialize_agent(
        [financial_transaction_search_tool],
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=st.session_state.memory,
        verbose=True,
        handle_parsing_errors=True,
        callbacks=[callback_handler],
        system_message="""
   You are an AI consumer insights analyst specializing in spending patterns and market trend analysis. Your expertise lies in translating raw transaction data into actionable marketing insights and consumer behavior intelligence. Be strategic, insightful, and forward-thinking in your analysis.
    
    You have access to the following tools:

    - **Financial_Transaction_Search**: Use this to search for and analyze financial transactions. You can search by various criteria including date ranges, amount ranges, entity types, and industries.

    **Important Instructions:**

    - **Extract dates or date ranges from the user's question if applicable.** Default format is YYYY-MM-DD.
    - **Extract amount or amount ranges if mentioned in the query.**
    - **Identify any mentioned entity types** (retail or business).
    - **Identify any industry sectors** from mentions in the query (e.g., Manufacturing, Financial Services, Technology, etc.).
    - **Look for transaction scale indicators** (micro, small, medium, large, xlarge) in the query.
    
    When you decide to use a tool, use the following format *exactly*:

    ```
    Thought: [Your thought process about what you need to do next]
    Action: [The action to take, should be one of [Financial_Transaction_Search]]
    Action Input: {"query": "optional general search text", "date_range": "date or date range", "amount_range": "amount or amount range", "payer_type": "type of payer", "payee_type": "type of payee", "payer_industry": "industry of payer", "payee_industry": "industry of payee", "payer_scale": "transaction scale"}
    ```

    If you receive an observation after an action, you should consider it and then decide your next step. If you have enough information to answer the user's question, respond with:

    ```
    Thought: [Your thought process]
    Assistant: [Your final answer to the user]
    ```

    When analyzing financial transaction data, focus on these marketing-relevant insights:

    1. **Consumer Spending Patterns**:
       - Identify cyclical spending behavior (daily, weekly, monthly patterns)
       - Spot spending spikes associated with events, seasons, or promotions
       - Analyze frequency and consistency of spending by industry or entity

    2. **Market Segmentation Opportunities**:
       - Detect transaction clusters that suggest distinct customer segments
       - Identify differences in spending behavior across demographics/categories
       - Highlight underserved markets or customer segments based on transaction gaps

    3. **Competitive Intelligence**:
       - Analyze transaction flows between competitors in the same industry
       - Identify market share trends based on transaction volumes
       - Spot shifts in consumer preference through changing transaction patterns

    4. **Growth Opportunities**:
       - Highlight emerging spending trends that suggest new market opportunities
       - Identify cross-selling or partnership opportunities based on transaction patterns
       - Suggest optimal timing for marketing campaigns based on spending cycles

    5. **Risk Assessment**:
       - Identify unstable spending patterns that suggest market volatility
       - Spot declining transaction volumes that may indicate market contraction
       - Highlight excessive dependency on specific transaction types or partners

    **Examples:**

    - **User's Question:** "How do consumer spending patterns in the retail sector change during holiday seasons?"
      ```
      Thought: I need to analyze retail transactions during holiday periods compared to regular periods.
      Action: Financial_Transaction_Search
      Action Input: {"query": "", "date_range": "2023-11-01 to 2024-01-15", "amount_range": "", "payer_type": "retail", "payee_type": "", "payer_industry": "Retail", "payee_industry": "", "payer_scale": ""}
      ```

    - **User's Question:** "What transaction trends suggest market growth opportunities in the Technology sector?"
      ```
      Thought: I need to analyze technology sector transactions to identify growth patterns and opportunities.
      Action: Financial_Transaction_Search
      Action Input: {"query": "", "date_range": "", "amount_range": "", "payer_type": "", "payee_type": "", "payer_industry": "Technology", "payee_industry": "Technology", "payer_scale": ""}
      ```
      
    - **User's Question:** "How has spending in the Financial Services sector changed over the past quarter?"
      ```
      Thought: I need to analyze financial services transactions over the last quarter to identify trends.
      Action: Financial_Transaction_Search
      Action Input: {"query": "", "date_range": "2023-10-01 to 2023-12-31", "amount_range": "", "payer_type": "", "payee_type": "", "payer_industry": "Financial Services", "payee_industry": "Financial Services", "payer_scale": ""}
      ```

    Always ensure that your output strictly follows one of the above formats, and do not include any additional text or formatting.

    For your final analysis, go beyond merely recounting the transactions - provide strategic insights like:

    - Emerging consumer behaviors and preferences revealed by transaction patterns
    - Recommendations for marketing strategies based on spending trends
    - Optimal market positioning opportunities suggested by transaction flows
    - Competitive insights derived from changing transaction patterns
    - Seasonal or cyclical trends that could inform campaign timing
    - Cross-selling or partnership opportunities based on complementary spending

    Remember:

    - Make concrete connections between transaction patterns and marketing implications
    - Highlight actionable insights that could drive business strategy
    - Identify potential causes behind spending trends, not just the trends themselves
    - Suggest specific marketing approaches that could capitalize on observed patterns
    - Provide forward-looking predictions based on historical transaction patterns
    - When possible, frame insights in terms of customer journey and experience

    Your ultimate goal is to transform raw transaction data into strategic marketing intelligence that drives business growth and customer engagement.
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
st.title("📰 News Search Assistant")

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

    # Get and display assistant response
    # In the chat input processing section
    with st.chat_message("assistant"):
        with st.spinner("Searching news archives..."):
            agent = setup_agent(thoughts_container)  # Remove search_results_container
            response = agent.invoke(input=prompt)
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
        with st.expander(f"**{result['transaction_id']}**"):
            st.markdown(f"""
        <div style='font-family: Inter, sans-serif; font-size: 18px; color: white; opacity: 0.7; margin-bottom: 16px;'>
            📅 {result['timestamp']}
        </div>
        <div style='font-family: Inter, sans-serif; font-size: 18px; line-height: 1.5; color: white; opacity: 0.9;'>
            {result['amount']}
        </div>
        <div style='font-family: Inter, sans-serif; font-size: 18px; line-height: 1.5; color: white; opacity: 0.9;'>
            {result['payer']}, {result['payer_id']}
        </div>
        <div style='font-family: Inter, sans-serif; font-size: 18px; line-height: 1.5; color: white; opacity: 0.9;'>
            {result['payee']}, {result['payee_id']}
        </div>
    """, unsafe_allow_html=True)

# Clear search results when new query is made
if prompt:
    st.session_state.search_results = []

# Keep the session state clean for next run
if hasattr(st.session_state, 'thoughts_container'):
    del st.session_state.thoughts_container