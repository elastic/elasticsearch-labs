import React, { useState } from "react";
import ChatInput from "./components/chat/input";

import { ChatMessageList } from "./components/chat_message_list";
import { Summary } from "./components/summary";
import SearchInput from "./components/chat/search_input";
import { SearchResponse } from "./types";
import {
  actions,
  isFacetSelected,
  thunkActions,
  useAppDispatch,
  useAppSelector,
} from "./store/provider";
import { cn } from "./lib/utils";
import { BeatLoader } from "react-spinners";
import { Header } from "./components/header";
import { SourceIcon } from "./components/source_icon";

function Results({ searchResponse }: { searchResponse: SearchResponse }) {
  const conversation = useAppSelector((state) => state.conversation);
  const streamMessage = useAppSelector((state) => state.streamMessage);
  const inProgressMessage = useAppSelector((state) => state.inProgressMessage);
  const filters = useAppSelector((state) => state.filters);
  const dispatch = useAppDispatch();

  const onSubmit = (query) => {
    dispatch(thunkActions.askQuestion(query));
  };

  const [summary, ...chatMessages] = conversation;

  return (
    <>
      <div className="max-w-2xl mx-auto relative">
        <div className="flex">
          <div className="absolute -left-60 top-4">
            {searchResponse.facets.map((facet) => (
              <div className="w-48" key={facet.name}>
                <h4 className="text-base font-bold leading-normal mb-2">
                  Filter results by source
                </h4>
                <div className="facet__entries">
                  {facet.entries.map((entry) => (
                    <div
                      className={cn(
                        "flex mb-0 content-center justify-between py-1 cursor-pointer hover:text-blue-700",
                        {
                          "text-blue-500 font-semibold": isFacetSelected(
                            filters,
                            facet.name,
                            entry.value
                          ),
                        }
                      )}
                      key={entry.value}
                      onClick={() => {
                        dispatch(
                          thunkActions.toggleFilter(facet.name, entry.value)
                        );
                      }}
                    >
                      <span className="flex-grow text-sm">{entry.value}</span>
                      <label className="justify-self-end bg-gray-200 rounded font-bold p-1 px-2 text-xs">
                        {entry.count}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white shadow-xl mt-4 p-6 rounded-xl border border-light-fog mb-8">
          <div className="mb-4">
            <Summary
              text={
                chatMessages.length === 0
                  ? streamMessage || summary?.content
                  : summary?.content
              }
              loading={inProgressMessage}
              sources={streamMessage && !summary ? [] : summary?.sources || []}
            />
          </div>

          <div
            className={cn("chat border-t border-fog", {
              "border-0": chatMessages.length === 0,
            })}
          >
            <div className="chat__messages">
              <ChatMessageList
                messages={chatMessages}
                incomingMessage={(summary && streamMessage) || null}
              />
            </div>
            <ChatInput isLoading={inProgressMessage} onSubmit={onSubmit} />
          </div>
        </div>
        <h3 className="text-lg mb-4 font-bold">Supporting search results</h3>
        <div className="">
          {searchResponse?.results.map((result) => (
            <div
              className="bg-white border border-light-fog mb-4 p-4 rounded-xl shadow-md"
              key={result.id}
            >
              <div className="flex flex-row space-x-1.5 pb-2">
                <SourceIcon icon={result.category[0].replace(" ", "_")} />
                <h4 className="text-md mb-1 font-semibold">{result.name[0]}</h4>
              </div>
              <p className="text-sm mb-2 text-light-ink">{result.summary[0]}</p>
              <a
                href={result.url[0]}
                className="text-sm text-dark-blue underline"
              >
                View document
              </a>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function App() {
  const dispatch = useAppDispatch();
  const searchResponse = useAppSelector((state) => state.searchResponse);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const loading = useAppSelector((state) => state.loading);

  const onSearch = (query) => {
    dispatch(actions.reset());
    dispatch(thunkActions.search(query, {}));
  };

  const suggestedQueries = [
    "What is our work from home policy?",
    "What's the NASA sales team?",
    "Does the company own my personal project?",
    "What job openings do we have?",
    "How does compensation work?",
  ];

  return (
    <>
      <Header />
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <SearchInput
            onSearch={onSearch}
            value={searchQuery}
            searchActive={searchResponse}
          />
        </div>

        {!loading && !searchResponse && (
          <div className="text-left mt-20 w-96 mx-auto">
            <h1 className="text-xl font-bold mb-4">Ask a question about</h1>
            <div className="flex flex-col space-y-4">
              {suggestedQueries.map((query) => (
                <a
                  href="#"
                  className="text-lg text-dark-blue hover:text-blue-700"
                  onClick={(e) => {
                    e.preventDefault();
                    setSearchQuery(query);
                    onSearch(query);
                  }}
                >
                  {query}
                </a>
              ))}
            </div>
          </div>
        )}

        {loading && !searchResponse && (
          <div className="relative w-24 mx-auto py-10 opacity-30">
            <BeatLoader size={15} />
          </div>
        )}

        {searchResponse && <Results searchResponse={searchResponse} />}
      </div>
    </>
  );
}

export default App;
