import { fetchEventSource } from '@microsoft/fetch-event-source'
import { ChatMessageType } from '../components/chat/message'
import { configureStore, createSlice } from '@reduxjs/toolkit'
import { Provider, useDispatch, useSelector } from 'react-redux'
import type { TypedUseSelectorHook } from 'react-redux'

type GlobalStateType = {
  loading: boolean
  conversation: ChatMessageType[]
  inProgressMessage: boolean
  sessionId: string | null
}

class RetriableError extends Error {}
class FatalError extends Error {}

const GLOBAL_STATE: GlobalStateType = {
  loading: false,
  conversation: [],
  inProgressMessage: false,
  sessionId: null,
}
const API_HOST = 'http://localhost:3001/api'

const globalSlice = createSlice({
  name: 'global',
  initialState: GLOBAL_STATE,
  reducers: {
    setSessionId: (state, action) => {
      state.sessionId = action.payload.sessionId
    },
    addConversation: (state, action) => {
      state.conversation.push(action.payload.conversation)
    },
    setConversation: (state, action) => {
      state.conversation = [action.payload.conversation]
    },
    updateConversation: (state, action) => {
      const conversationIndex = state.conversation.findIndex(
        (c) => c.id === action.payload.id
      )

      if (conversationIndex !== -1) {
        state.conversation[conversationIndex] = {
          ...state.conversation[conversationIndex],
          ...action.payload,
        }
      }
    },
    setLoading: (state, action) => {
      state.loading = action.payload.loading
    },
    setInProgressMessage: (state, action) => {
      state.inProgressMessage = action.payload.inProgressMessage
    },
    reset: (state) => {
      state.sessionId = null
      state.inProgressMessage = false
      state.conversation = []
    },
  },
})

const store = configureStore({
  reducer: globalSlice.reducer,
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
export const useAppDispatch: () => AppDispatch = useDispatch
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector
export const actions = globalSlice.actions

export const hasStartedConversation = (state: RootState) => {
  const [summary, ...conversation] = state.conversation
  return conversation.length > 0
}

export const thunkActions = {
  search: (query: string) => {
    return async function fetchSearch(dispatch) {
      dispatch(actions.reset())

      dispatch(actions.setLoading({ loading: true }))
      dispatch(thunkActions.chat(query))
    }
  },
  askQuestion: (question: string, signal) => {
    return async function askQuestion(dispatch, getState) {
      const state = getState()
      dispatch(
        actions.addConversation({
          conversation: {
            isHuman: true,
            content: question,
            id: state.conversation.length + 1,
          },
        })
      )
      dispatch(thunkActions.chat(question, signal))
    }
  },
  chat: (question: string, signal?: AbortSignal) => {
    return async function fetchSearch(dispatch, getState) {
      if (getState().inProgressMessage) {
        return
      }

      let message = ''
      const sessionId = getState().sessionId
      const sourcesMap: Map<
        string,
        { name: string; url?: string; summary: string[] }
      > = new Map()
      // const action = hasStartedConversation(getState())
      //   ? actions.addConversation
      //   : actions.setConversation
      const conversationId = getState().conversation.length + 1
      dispatch(
        actions.addConversation({
          conversation: {
            loading: true,
            isHuman: false,
            content: '',
            id: conversationId,
          },
        })
      )
      dispatch(actions.setInProgressMessage({ inProgressMessage: true }))
      let countRetiresError = 0

      await fetchEventSource(
        `${API_HOST}/chat${sessionId ? `?session_id=${sessionId}` : ''}`,
        {
          method: 'POST',
          openWhenHidden: true,
          body: JSON.stringify({
            question,
          }),
          headers: {
            'Content-Type': 'application/json',
          },
          signal,
          async onmessage(event) {
            if (event.event === 'FatalError') {
              throw new FatalError(event.data)
            }

            if (event.data.startsWith('[SESSION_ID]')) {
              const sessionId = event.data.split(' ')[1].trim()
              dispatch(actions.setSessionId({ sessionId }))
            } else if (event.data.startsWith('[SOURCE]')) {
              const source = event.data.replace('[SOURCE] ', '') //event.data.match(/\[SOURCE\] ([^]+?)(?=\[|$)/)?.[1]

              try {
                if (source) {
                  const parsedSource = JSON.parse(source.replaceAll('\n', ''))

                  if (sourcesMap.has(parsedSource.name)) {
                    const source = sourcesMap.get(parsedSource.name)!

                    source.summary = [
                      ...source.summary,
                      parsedSource.page_content,
                    ]
                  } else {
                    sourcesMap.set(parsedSource.name, {
                      ...parsedSource,
                      summary: [parsedSource.page_content],
                    })
                  }
                }
              } catch (e) {
                console.log('error', source, event.data)
                console.error(e)
              }
            } else if (event.data === '[DONE]') {
              dispatch(
                actions.updateConversation({
                  id: conversationId,
                  sources: Array.from(sourcesMap.values()),
                })
              )
              dispatch(
                actions.setInProgressMessage({ inProgressMessage: false })
              )
            } else {
              message += message && event.data === '' ? '\n' : event.data

              dispatch(
                actions.updateConversation({
                  id: conversationId,
                  content: message,
                  loading: false,
                })
              )
              dispatch(actions.setLoading({ loading: false }))
            }
          },
          async onopen(response) {
            if (response.ok) {
              return
            } else if (
              response.status >= 400 &&
              response.status < 500 &&
              response.status !== 429
            ) {
              throw new FatalError()
            } else {
              throw new RetriableError()
            }
          },
          onerror(err) {
            if (err instanceof FatalError || countRetiresError > 3) {
              dispatch(actions.setLoading({ loading: false }))

              throw err
            } else {
              countRetiresError++
              console.error(err)
            }
          },
        }
      )
    }
  },
}

export const GlobalStateProvider = ({ children }) => {
  return <Provider store={store}>{children}</Provider>
}
