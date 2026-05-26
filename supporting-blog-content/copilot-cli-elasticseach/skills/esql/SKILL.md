---
name: esql
description: Interact with Elasticsearch using ES|QL and natural language.
---
# ES|QL Skill

When invoked, act as a translator between natural language and Elasticsearch Query Language (ES|QL). 

1. Analyze the user's request to understand the desired data, filters, and aggregations.
2. Use the `platform_core.get_index_mapping` tool if you need to verify the fields in the target index.
3. Formulate the ES|QL query. 
4. Execute the query using the `platform_core.execute_esql` tool.
5. Present the results back to the user in a clear, readable Markdown table, explaining any notable patterns if requested.
