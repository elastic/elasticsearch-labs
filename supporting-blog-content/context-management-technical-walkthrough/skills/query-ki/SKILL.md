---
name: query-ki
description: >-
  Retrieve Knowledge Indicators (pre-computed context) from the Elasticsearch AI
  Index before answering. Use it to find which index to search (routing profiles)
  or to look up pre-computed facts without reading source documents. Trigger on any question that depends on specific facts, names, dates, or on choosing a data source.
allowed-tools: esql_query
---

# Retrieving Knowledge Indicators

Knowledge Indicators (KIs) live in Elasticsearch indices named `ai-index-*`.
Retrieve them by calling the `esql_query` tool with the query below. Substitute
the user's question for `<query>`, and choose the KI type you need: `corpus_entry`
for facts, `index_metadata_entry` for routing profiles.

```esql
FROM ai-index-idx-* METADATA _id, _index, _score
| WHERE type == "<ki_type>"
| FORK
    (WHERE MATCH(content, "<query>") OR MATCH(description, "<query>")
     | SORT _score DESC | LIMIT 20)
    (WHERE content.semantic : "<query>"
     | SORT _score DESC | LIMIT 20)
| FUSE
| SORT _score DESC
| KEEP title, content, description, tags
| LIMIT 5
```

Ground your answer in what the query returns, and cite the KI titles you used. If
nothing relevant comes back, say so rather than guessing.
