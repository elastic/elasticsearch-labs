import React, { Fragment, useState } from 'react'

import {
  AppStatus,
  thunkActions,
  useAppDispatch,
  useAppSelector,
} from 'store/provider'
import { Header } from 'components/header'
import { Loader } from 'components/loader'
import { Chat } from 'components/chat/chat'
import SearchInput from 'components/search_input'

const App = () => {
  const dispatch = useAppDispatch()
  const status = useAppSelector((state) => state.status)
  const [summary, ...messages] = useAppSelector((state) => state.conversation)
  const hasSummary = useAppSelector(
    (state) => !!state.conversation?.[0]?.content
  )
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [controller, setController] = useState<AbortController>()

  const getRequestSignal = () => {
    const newController = new AbortController()

    setController(newController)

    return newController.signal
  }
  const handleSearch = (query: string) => {
    dispatch(thunkActions.search(query, getRequestSignal()))
  }
  const handleSendChatMessage = (query: string) => {
    dispatch(thunkActions.askQuestion(query, getRequestSignal()))
  }
  const handleAbortRequest = () => {
    controller?.abort()
    dispatch(thunkActions.stopRequest())
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
            onSearch={handleSearch}
            value={searchQuery}
            appStatus={status}
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
                    handleSearch(query)
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
              <div className="max-w-2xl mx-auto relative">
                <Chat
                  status={status}
                  messages={messages}
                  summary={summary}
                  onSend={handleSendChatMessage}
                  onAbortRequest={handleAbortRequest}
                />

                {!!summary?.sources?.length && (
                  <>
                    <h3 className="text-lg mb-4 font-bold">Sources chunks</h3>
                    <div className="">
                      {summary?.sources?.map((result) => (
                        <div
                          className="bg-white border border-light-fog mb-4 p-4 rounded-xl shadow-md"
                          key={result.name}
                        >
                          <h4 className="flex flex-row space-x-1.5 pb-2 text-md mb-1 font-semibold">
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

                          {result.summary?.map((text, index) => (
                            <Fragment key={index}>
                              {!!index && <p>...</p>}
                              <p className="text-sm mb-2 text-light-ink">
                                {text}
                              </p>
                            </Fragment>
                          ))}
                        </div>
                      ))}
                    </div>
                  </>
                )}
              </div>
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
