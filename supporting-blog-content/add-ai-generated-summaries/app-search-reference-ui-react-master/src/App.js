import React from "react";
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {
  ErrorBoundary,
  SearchProvider,
  SearchBox,
  Results,
  Facet,
} from "@elastic/react-search-ui";
import { Layout } from "@elastic/react-search-ui-views";
import "@elastic/react-search-ui-views/lib/styles/styles.css";
import AiSummary from "./AiSummary";

const connector = new ElasticsearchAPIConnector(
  {
    host: "http://localhost:1337/api",
    index: "search-labs-index",
  },
  (requestBody, requestState) => {
    if (!requestState.searchTerm) return requestBody;
    requestBody.query = {
      semantic: {
        query: requestState.searchTerm,
        field: "semantic_text",
      },
    };
    return requestBody;
  }
);

const config = {
  debug: true,
  searchQuery: {
    search_fields: {
      semantic_text: {},
    },
    result_fields: {
      title: {
        snippet: {},
      },
      article_content: {
        snippet: {
          size: 10,
        },
      },
      meta_description: {},
      url: {},
      meta_author: {},
      meta_img: {},
    },
    facets: {
      "meta_author.enum": { type: "value" },
    },
  },
  apiConnector: connector,
  alwaysSearchOnInitialLoad: false,
};

export default function App() {
  return (
    <SearchProvider config={config}>
      <div className="App">
        <ErrorBoundary>
          <Layout
            header={<SearchBox />}
            bodyHeader={<AiSummary />}
            bodyContent={
              <Results
                titleField="title"
                thumbnailField="meta_img"
                urlField="url"
              />
            }
            sideContent={
              <Facet key={"1"} field={"meta_author.enum"} label={"author"} />
            }
          />
        </ErrorBoundary>
      </div>
    </SearchProvider>
  );
}
