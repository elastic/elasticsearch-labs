import React, { useState } from 'react'
import ChatInput from './components/chat/input'

import { ChatMessageList } from './components/chat/message_list'
import { Summary } from './components/summary'
import SearchInput from './components/chat/search_input'
import {
  AppStatus,
  thunkActions,
  useAppDispatch,
  useAppSelector,
} from './store/provider'
import { cn } from './lib/utils'
import { Header } from './components/header'
import { Loader } from './components/loader'

function Results() {
  const conversation = useAppSelector((state) => state.conversation)
  const status = useAppSelector((state) => state.status)
  const dispatch = useAppDispatch()

  const onSubmit = (query, signal) => {
    dispatch(thunkActions.askQuestion(query, signal))
  }
  const onAbortRequest = () => {
    dispatch(thunkActions.stopRequest())
  }

  const [summary, ...chatMessages] = conversation

  return (
    <>
      <div className="max-w-2xl mx-auto relative">
        <div className="bg-white shadow-xl mt-4 p-6 rounded-xl border border-light-fog mb-8">
          <div className="mb-4">
            <Summary text={summary?.content} sources={summary?.sources || []} />
          </div>

          <div
            className={cn('chat border-t border-fog', {
              'border-0': chatMessages.length === 0,
            })}
          >
            <div className="chat__messages">
              <ChatMessageList
                messages={chatMessages}
                isMessageLoading={status === AppStatus.StreamingMessage}
              />
            </div>
            <ChatInput
              isMessageLoading={status === AppStatus.StreamingMessage}
              onSubmit={onSubmit}
              onAbortRequest={onAbortRequest}
            />
          </div>
        </div>
        {!!summary?.sources?.length && (
          <>
            <h3 className="text-lg mb-4 font-bold">Sources chunks</h3>
            <div className="">
              {summary?.sources?.map((result) => (
                <div
                  className="bg-white border border-light-fog mb-4 p-4 rounded-xl shadow-md"
                  key={result.name}
                >
                  <div className="flex flex-row space-x-1.5 pb-2">
                    <h4 className="text-md mb-1 font-semibold">
                      {result.url ? (
                        <a
                          className="hover:text-blue text-dark-blue"
                          href={result?.url}
                        >
                          {result.name}
                        </a>
                      ) : (
                        result.name
                      )}
                    </h4>
                  </div>
                  {result.summary?.map((text, index) => (
                    <React.Fragment key={index}>
                      {!!index && <p>...</p>}
                      <p className="text-sm mb-2 text-light-ink">{text}</p>
                    </React.Fragment>
                  ))}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </>
  )
}

function App() {
  const dispatch = useAppDispatch()
  const status = useAppSelector((state) => state.status)
  const hasSummary = useAppSelector(
    (state) => !!state.conversation?.[0]?.content
  )
  const [searchQuery, setSearchQuery] = useState<string>('')

  const onSearch = (query) => {
    dispatch(thunkActions.search(query))
  }

  const suggestedQueries = [
    'What is our work from home policy?',
    "What's the NASA sales team?",
    'Does the company own my personal project?',
    'What job openings do we have?',
    'How does compensation work?',
  ]

  return (
    <>
      <Header />
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <SearchInput
            onSearch={onSearch}
            value={searchQuery}
            searchActive={status !== AppStatus.Idle}
          />
        </div>

        {status === AppStatus.Idle ? (
          <div className="text-left mt-20 w-96 mx-auto">
            <h1 className="text-xl font-bold mb-4">Ask a question about</h1>
            <div className="flex flex-col space-y-4">
              {suggestedQueries.map((query) => (
                <a
                  key={query}
                  href="#"
                  className="text-lg text-dark-blue hover:text-blue-700"
                  onClick={(e) => {
                    e.preventDefault()
                    setSearchQuery(query)
                    onSearch(query)
                  }}
                >
                  {query}
                </a>
              ))}
            </div>
          </div>
        ) : (
          <>
            {hasSummary ? (
              <Results />
            ) : (
              <Loader className="relative w-24 mx-auto py-10 opacity-30" />
            )}
          </>
        )}
      </div>
    </>
  )
}

export default App
