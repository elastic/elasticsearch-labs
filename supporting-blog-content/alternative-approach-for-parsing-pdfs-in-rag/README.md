
# PDF Parsing - Table Extraction

 Python notebook demonstrates an alternative approach to parsing PDFs, particularly focusing on extracting and converting tables into a format suitable for search applications such as Retrieval-Augmented Generation (RAG). The notebook leverages Azure OpenAI to process and convert table data from PDFs into plain text for better searchability and indexing.

## Features
- **PDF Table Extraction**: The notebook identifies and parses tables from PDFs.
- **LLM Integration**: Calls Azure OpenAI models to provide a text representation of the extracted tables.
- **Search Optimization**: The parsed table data is processed into a format that can be more easily indexed and searched in Elasticsearch or other vector-based search systems.
  
## Getting Started

### Prerequisites
- Python 3.x
- Output Directory
  - Example
    - `/tmp`
  - Parsed output file name
    - Example
      - `parsed_file.txt`
- Azure Account
  - OpenAI deployment
  - Key
    - Example
      - a330xxxxxxxde9xxxxxx
  - Completions endpoint such as GPT-4o
    - Example
      - https://exampledeploy.openai.azure.com/openai/deployments/gpt-35-turbo-16k/chat/completions?api-version=2024-08-01-preview
  - For more information on getting started with Azure OpenAI, check out the official [Azure OpenAI ChatGPT Quickstart](https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=command-line%2Ctypescript%2Cpython-new&pivots=programming-language-studio).


## Example Use Case
This notebook is ideal for use cases where PDFs contain structured tables that need to be converted into plain text for indexing and search applications in environments like Elasticsearch or similar search systems.

