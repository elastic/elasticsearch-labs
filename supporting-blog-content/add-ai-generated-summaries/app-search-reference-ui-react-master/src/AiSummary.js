import { withSearch } from "@elastic/react-search-ui";
import { useState, useEffect } from "react";
import axios from "axios";
import { Card } from "antd";
import parse from "html-react-parser";

const formatSearchResults = (results) => {
  return results
    .slice(0, 3)
    .map(
      (result) => `
    Article Author(s): ${result.meta_author.raw.join(",")}
    Article URL: ${result.url.raw}
    Article title: ${result.title.raw}
    Article content: ${result.article_content.raw}
  `
    )
    .join("\n");
};

const fetchAiSummary = async (searchTerm, results) => {
  const prompt = `
    You are a search assistant. Your mission is to complement search results with an AI Summary to address the user request.
    User request: ${searchTerm}
    Top search results: ${formatSearchResults(results)}
    Rules:
    - The answer must be short. No more than one paragraph.
    - Use HTML
    - Use content from the most relevant search results only to answer the user request
    - Add highlights wrapping in <i><b></b></i> tags the most important phrases of your answer
    - At the end of the answer add a citations section with links to the articles you got the answer on this format:
    <h4>Citations</h4>
    <ul>
      <li><a href="{url}"> {title} </a></li>
    </ul>
    - Only provide citations from the top search results I showed you, and only if they are relevant to the user request.
  `;
  const responseData = await axios.post(
    "http://localhost:1337/api/completion",
    { input: prompt },
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  return responseData.data.completion[0].result;
};

const AiSummary = ({ results, searchTerm, resultSearchTerm }) => {
  const [aiSummary, setAiSummary] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (searchTerm) {
      setIsLoading(true);
      fetchAiSummary(searchTerm, results).then((summary) => {
        setAiSummary(summary);
        setIsLoading(false);
      });
    }
  }, [resultSearchTerm]);

  return (
    <Card style={{ width: "100%" }} loading={isLoading}>
      <div>
        <h2>AI Summary</h2>
        {!resultSearchTerm ? "Ask anything!" : parse(aiSummary)}
      </div>
    </Card>
  );
};

export default withSearch(({ results, searchTerm, resultSearchTerm }) => ({
  results,
  searchTerm,
  resultSearchTerm,
  AiSummary,
}))(AiSummary);
