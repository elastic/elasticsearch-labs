package elasticsearch

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"

	"github.com/elastic/go-elasticsearch/v8"
	"github.com/elastic/go-elasticsearch/v8/typedapi/types"
)

// Initializing elasticsearch client

func EsClient() (*elasticsearch.TypedClient, error) {
	var cloudID = "" // your Elastic Cloud ID Here
	var apiKey = ""  // your Elastic ApiKey Here

	es, err := elasticsearch.NewTypedClient(elasticsearch.Config{
		CloudID: cloudID,
		APIKey:  apiKey,
	})

	if err != nil {
		return nil, fmt.Errorf("unable to connect: %w", err)
	}
	return es, nil
}

// Searching for documents and building the context
func SemanticRetriever(client *elasticsearch.TypedClient, query string, size int) (string, error) {
	// Perform the semantic search
	res, err := client.Search().
		Index("rag-ollama").
		Query(&types.Query{
			Semantic: &types.SemanticQuery{
				Field: "semantic_field",
				Query: query,
			},
		}).
		Size(size).
		Do(context.Background())

	if err != nil {
		return "", fmt.Errorf("semantic search failed: %w", err)
	}

	// Prepare to format the results
	var output strings.Builder
	output.WriteString("Documents found\n\n")

	// Iterate through the search hits
	for i, hit := range res.Hits.Hits {
		// Define a struct to unmarshal each document
		var doc struct {
			Title   string `json:"title"`
			Content string `json:"content"`
		}

		// Unmarshal the document source into our struct
		if err := json.Unmarshal(hit.Source_, &doc); err != nil {
			return "", fmt.Errorf("failed to unmarshal document %d: %w", i, err)
		}

		// Append the formatted document to our output
		output.WriteString(fmt.Sprintf("Title\n%s\n\nContent\n%s\n", doc.Title, doc.Content))

		// Add a separator between documents, except for the last one
		if i < len(res.Hits.Hits)-1 {
			output.WriteString("\n-----\n\n")
		}
	}

	// Return the formatted output as a string
	return output.String(), nil
}
