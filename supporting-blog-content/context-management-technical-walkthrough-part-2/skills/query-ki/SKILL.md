---
name: query-ki
description: >-
  Retrieve Knowledge Indicators (pre-computed context) from the Elasticsearch AI
  Index before answering. Use it to look up pre-computed facts without reading
  source documents. Trigger on any question that depends on specific facts,
  names, dates, or events.
allowed-tools: esql_query
---

# Retrieving Knowledge Indicators

Knowledge Indicators (KIs) live in Elasticsearch indices named `ai-index-*`.
Retrieve them by calling the `esql_query` tool with the query below. Substitute
the user's question for `<query>`, and use `corpus_entry` as the `<ki_type>` for
document facts.

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
