import { thunkActions, useAppDispatch, useAppSelector } from './store/provider'
import { InlineChat } from './inline_chat'
import { ReactComponent as ElasticLogo } from 'images/elastic_logo.svg'
import './inline_chat.css'

const InlineApp = () => {
  const dispatch = useAppDispatch()
  const status = useAppSelector((state) => state.status)
  const messages = useAppSelector((state) => state.conversation)
  const handleSendChatMessage = (query: string) => {
    dispatch(thunkActions.askQuestion(query))
  }
  const handleAbortRequest = () => {
    dispatch(thunkActions.abortRequest())
  }
  const handleSourceClick = ({ url }) => {
    window.open(url, '_blank', 'noreferrer')
  }

  return (
    <div className="bg-white p-4 h-screen flex flex-col">
      <h1 className="text-lg font-bold text-gray-500 m-2 inline-flex items-center">
        <ElasticLogo className="w-8 h-8 mr-2" />
        Elastic doc helper
      </h1>
      <InlineChat
        status={status}
        messages={messages}
        onSend={handleSendChatMessage}
        onAbortRequest={handleAbortRequest}
        onSourceClick={handleSourceClick}
      />
      <p className="text-zinc-400 text-sm font-medium text-right mt-1">
        Powered by <b>Elasticsearch</b> with <b>Azure OpenAI</b>
      </p>
    </div>
  )
}

export default InlineApp
