# You know, for Context\! 

## The power of Hybrid Search in Context Engineering

There are a multitude of ways to query your content for providing context to generative and agentic AI operations. Here are a few examples to get you started and please check back later as we continue to update these techniques for supporting context engineering\!

1. Non-content signals  
   1. [ES|QL biasing](#es|ql-biasing)  
   2. [Aggregations](#aggregations)  
2. Agents & Tools (coming soon\!)

# Non-content signals

## ES|QL biasing

Combining `FORK`/`FUSE`, `RERANK`, and `INLINE STATS` in a single ES|QL query allows for some very powerful and nuanced search strategies. Here are a few scenarios that demonstrate how you can use these techniques together to leverage non-content signals.

## Scenario 1: Boosting Recently Published and Popular Content

Imagine you have a knowledge base of articles. You want to find articles relevant to a user's query, but you also want to boost articles that are both recent and have been found helpful by other users (e.g., have a high "likes" count).

In this scenario, we can use a hybrid search to find relevant articles and then rerank them based on a combination of their publication date and popularity.

```sql
FROM articles
| FORK
    (WHERE MATCH(content, "elasticsearch performance tuning"))
    (WHERE QSTR("content:elasticsearch AND content:performance"))
| FUSE
| INLINE STATS avg_likes = AVG(likes), max_likes = MAX(likes)
| EVAL recency_factor = CASE(
    publication_date > NOW() - 30 days, 1.5,
    publication_date > NOW() - 90 days, 1.2,
    1.0
  )
| EVAL popularity_factor = CASE(
    likes > avg_likes * 1.5, 1.3,
    likes > avg_likes, 1.1,
    1.0
  )
| EVAL boost_score = recency_factor * popularity_factor
| RERANK 50 boost_score
| LIMIT 20
```

Here's what's happening in this query:

1. **FORK**: Creates two parallel search paths \- one using MATCH and one using QSTR for different retrieval strategies  
2. **FUSE**: Combines results using Reciprocal Rank Fusion as the default reranking method  
3. **INLINE STATS**: Calculates avg\_likes and max\_likes across the fused result set, making these values available to each row  
4. **EVAL**: Creates boost factors based on recency and popularity (using the inline stats)  
5. **RERANK 50 boost\_score**: Reranks the top 50 documents by the calculated boost\_score

This approach ensures that relevant, recent, and popular articles are prioritized.

## Scenario 2: E-commerce Search with Sales and Stock Adjustment

In an e-commerce setting, you want to show customers products that match their search term, but you also want to promote products that are selling well and are in stock. You might also want to down-rank products with low stock to avoid customer frustration.

```sql
FROM products
| FORK
    (WHERE MATCH(description, "running shoes"))
    (WHERE MATCH(title, "running shoes") | EVAL boost = 1.2)
    (WHERE MATCH(category, "athletic footwear"))
| FUSE
| INLINE STATS 
    avg_sales = AVG(monthly_sales),
    stddev_sales = STDDEV(monthly_sales),
    avg_stock = AVG(stock_level)
| EVAL sales_zscore = (monthly_sales - avg_sales) / stddev_sales
| EVAL sales_factor = CASE(
    sales_zscore > 2.0, 2.5,
    sales_zscore > 1.0, 1.8,
    sales_zscore > 0, 1.2,
    1.0
  )
| EVAL stock_factor = CASE(
    stock_level < 5, 0.3,
    stock_level < avg_stock * 0.5, 0.7,
    1.0
  )
| EVAL inventory_score = sales_factor * stock_factor
| RERANK 100 inventory_score
| LIMIT 50
```

In this e-commerce query:

1. **FORK**: Three parallel searches \- description match, title match (with boost), and category match  
2. **FUSE**: Combines all three result sets using RRF as the default reranking method  
3. **INLINE STATS**: Calculates sales statistics (average and standard deviation) and average stock across results  
4. **EVAL**: Computes z-score for sales to identify outliers, then creates factors for both sales performance and stock availability  
5. **RERANK 100 inventory\_score**: Reranks top 100 by the combined inventory score that balances sales velocity with stock availability

This helps customers find what they want while also aligning the search results with business goals like moving popular inventory and managing stock.

## Scenario 3: Prioritizing High-Severity Issues in a Bug Tracker

For a software development team, when searching for issues, it's crucial to surface high-severity, high-priority, and recently updated issues first.

```sql
FROM issues
| FORK
    (WHERE MATCH(title, "authentication bug"))
    (WHERE MATCH(description, "authentication bug"))
    (WHERE MATCH(tags, "authentication") AND status == "open")
| FUSE
| INLINE STATS 
    avg_comments = AVG(comment_count),
    p75_comments = PERCENTILE(comment_count, 75),
    avg_age_days = AVG((NOW() - created_date) / 1 day)
| EVAL severity_weight = CASE(
    severity == "Critical", 10.0,
    severity == "High", 5.0,
    severity == "Medium", 2.0,
    1.0
  )
| EVAL activity_weight = CASE(
    comment_count > p75_comments, 2.0,
    comment_count > avg_comments, 1.5,
    1.0
  )
| EVAL recency_weight = CASE(
    last_updated > NOW() - 7 days, 2.0,
    last_updated > NOW() - 14 days, 1.5,
    last_updated > NOW() - 30 days, 1.2,
    0.8
  )
| EVAL priority_score = (severity_weight * 3) + activity_weight + recency_weight
| RERANK 75 priority_score
| LIMIT 25
```

In this issue tracking query:

1. **FORK**: Three search strategies \- title match, description match, and tag+status filter  
2. **FUSE**: Merges results from all three approaches using RRF as the default reranking method  
3. **INLINE STATS**: Calculates comment statistics (average and 75th percentile) and average issue age  
4. **EVAL**: Creates weighted scores for severity (heavily weighted), activity level (using percentile from inline stats), and recency  
5. **RERANK 75 priority\_score**: Reranks top 75 issues by the additive priority score that emphasizes severity while considering community engagement and recent activity

This additive scoring model allows you to weigh different factors independently, ensuring that the most critical and actively discussed issues rise to the top.

\_\_\_\_\_

## Aggregations

Elasticsearch aggregations are powerful tools for enriching LLM context in agentic AI systems. They are currently supported only in the Elasticsearch Query DSL, and they can be used either in conjunction with hybrid search queries, or perhaps from agentic tool calls that are used to influence the LLMs considerations of context received through other data calls. 

**Key Benefits for LLM/Agent Systems:**

1\. **Token Efficiency**: Reduce 100K documents to a few hundred tokens of aggregated insights  
2\. **Structured Context**: Provide numerical facts that LLMs can reason about accurately  
3\. **Multi-Level Detail**: Use nested aggregations for hierarchical understanding  
4\. **Real-Time Insights**: Aggregations run on current data, keeping agents up-to-date  
5\. **Hybrid Approach**: Combine aggregated statistics with semantic search results for comprehensive context

### Architecture Pattern:

This approach gives your LLM both the "what" (relevant documents) and the "how much/how many" (aggregated metrics) for more informed responses\!

```
User Query → Vector Search (semantic relevance) 
           → Aggregations (statistical context)
          → Combine both → LLM Context Window
          → Generate Response
```

Here are practical examples of how you can use them:  
\-----

## 1\. Summarizing Large Datasets for Context Compression

Instead of sending thousands of raw documents to an LLM, use aggregations to create concise summaries:

```json
POST /customer-feedback/_search
{
  "size": 0,
  "aggs": {
    "sentiment_distribution": {
      "terms": {
        "field": "sentiment",
        "size": 10
      }
    },
    "avg_rating": {
      "avg": {
        "field": "rating"
      }
    },
    "top_issues": {
      "terms": {
        "field": "issue_category",
        "size": 5
      },
      "aggs": {
        "avg_severity": {
          "avg": {
            "field": "severity_score"
          }
        }
      }
    }
  }
}
```

**Use case**: Provide the LLM with "80% of feedback is positive, average rating is 4.2, top issue is 'shipping delays' with severity 3.5" instead of 10,000 individual reviews.

## 2\. Time-Series Trend Analysis for Temporal Context

Help LLMs understand patterns over time:

```json
POST /application-logs/_search
{
  "size": 0,
  "aggs": {
    "errors_over_time": {
      "date_histogram": {
        "field": "@timestamp",
        "fixed_interval": "1h"
      },
      "aggs": {
        "error_types": {
          "terms": {
            "field": "error.type",
            "size": 3
          }
        },
        "avg_response_time": {
          "avg": {
            "field": "response_time_ms"
          }
        }
      }
    }
  }
}
```

**Use case**: Give the LLM context like "Error rate spiked 300% at 2pm, primarily 'timeout' errors, coinciding with 2x slower response times."

3\. Categorical Breakdown for Multi-Dimensional Analysis  
Use nested aggregations to provide hierarchical context:

```json
POST /sales-data/_search
{
  "size": 0,
  "aggs": {
    "by_region": {
      "terms": {
        "field": "region",
        "size": 10
      },
      "aggs": {
        "by_product_category": {
          "terms": {
            "field": "product.category",
            "size": 5
          },
          "aggs": {
            "total_revenue": {
              "sum": {
                "field": "revenue"
              }
            },
            "avg_order_value": {
              "avg": {
                "field": "order_value"
              }
            }
          }
        }
      }
    }
  }
}
```

**Use case**: Provide structured insights like "In EMEA, Electronics generated $2M with $450 avg order value, while in APAC, Clothing led with $1.8M."

4\. Statistical Context for Anomaly Detection  
Use percentile and stats aggregations to help LLMs understand what's "normal":

```json
POST /system-metrics/_search
{
  "size": 0,
  "aggs": {
    "cpu_stats": {
      "stats": {
        "field": "cpu_usage_percent"
      }
    },
    "cpu_percentiles": {
      "percentiles": {
        "field": "cpu_usage_percent",
        "percents": [50, 90, 95, 99]
      }
    },
    "outliers": {
      "filter": {
        "range": {
          "cpu_usage_percent": {
            "gte": 95
          }
        }
      },
      "aggs": {
        "affected_hosts": {
          "terms": {
            "field": "host.name",
            "size": 10
          }
        }
      }
    }
  }
}
```

**Use case**: Tell the LLM "Normal CPU is 45% (p50) with p99 at 78%. Current 96% usage on host-prod-03 is anomalous."

5\. Cardinality for Uniqueness Insights  
Understand the diversity of your data:

```json
POST /user-sessions/_search
{
  "size": 0,
  "aggs": {
    "unique_users": {
      "cardinality": {
        "field": "user_id"
      }
    },
    "unique_pages_visited": {
      "cardinality": {
        "field": "page_url"
      }
    },
    "session_duration_avg": {
      "avg": {
        "field": "session_duration_seconds"
      }
    }
  }
}
```

**Use case**: Provide context like "15,234 unique users visited 342 unique pages with avg session of 4.2 minutes."

6\. Top Hits for Representative Examples  
Combine aggregations with actual document samples:

```json
POST /support-tickets/_search
{
  "size": 0,
  "aggs": {
    "by_priority": {
      "terms": {
        "field": "priority",
        "size": 5
      },
      "aggs": {
        "sample_tickets": {
          "top_hits": {
            "size": 2,
            "_source": ["ticket_id", "subject", "description"],
            "sort": [{"created_at": "desc"}]
          }
        },
        "avg_resolution_time": {
          "avg": {
            "field": "resolution_time_hours"
          }
        }
      }
    }
  }
}
```

**Use case**: Give the LLM both statistics AND concrete examples: "23 critical tickets (avg 2.1hr resolution). Example: 'Database connection pool exhausted'."

7\. Significant Terms for Anomaly Context  
Find what's unusual about a subset of data:

```json
POST /security-logs/_search
{
  "query": {
    "term": {
      "event.outcome": "failure"
    }
  },
  "size": 0,
  "aggs": {
    "significant_failure_reasons": {
      "significant_terms": {
        "field": "error.message.keyword",
        "size": 10
      }
    }
  }
}
```

**Use case**: Tell the LLM "Failed logins show unusual pattern: 'invalid\_token' appears 15x more than normal, suggesting credential stuffing attack."

8\. Composite Aggregations for Pagination  
Handle large cardinality data for iterative agent processing:

```json
POST /product-catalog/_search
{
  "size": 0,
  "aggs": {
    "products_by_category_and_brand": {
      "composite": {
        "size": 100,
        "sources": [
          {"category": {"terms": {"field": "category"}}},
          {"brand": {"terms": {"field": "brand"}}}
        ]
      },
      "aggs": {
        "avg_price": {
          "avg": {
            "field": "price"
          }
        }
      }
    }
  }
}
```

**Use case**: Allow agents to iteratively process large datasets in chunks while maintaining aggregated context.

