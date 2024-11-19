package main

import (
	"fmt"
	"log"
	"ollama-rag/elasticsearch"

	"github.com/parakeet-nest/parakeet/completion"
	"github.com/parakeet-nest/parakeet/enums/option"
	"github.com/parakeet-nest/parakeet/llm"
)

func main() {

	ollamaUrl := "http://localhost:11434"
	chatModel := "llama3.2:latest"
	question := `Summarize document: JAK Inhibitors vs. Monoclonal Antibodies in Rheumatoid Arthritis Treatment`
	size := 3

	esClient, err := elasticsearch.EsClient()

	if err != nil {
		log.Fatalln("😡:", err)
	}

	// Retrieve documents from semantic query to build context
	documentsContent, nil := elasticsearch.SemanticRetriever(esClient, question, size)

	systemContent := `You are a helpful medical assistant. Only answer the questions based on found documents.
	Add references to the base document titles and be succint in your answers.`

	options := llm.SetOptions(map[string]interface{}{
		option.Temperature: 0.0,
	})

	queryChat := llm.Query{
		Model: chatModel,
		Messages: []llm.Message{
			{Role: "system", Content: systemContent},
			{Role: "system", Content: documentsContent},
			{Role: "user", Content: question},
		},
		Options: options,
	}

	fmt.Println()
	fmt.Println("🤖 answer:")

	// Answer the question
	_, err = completion.ChatStream(ollamaUrl, queryChat,
		func(answer llm.Answer) error {
			fmt.Print(answer.Message.Content)
			return nil
		})
	if err != nil {
		log.Fatal("😡:", err)
	}

	fmt.Println()
}
