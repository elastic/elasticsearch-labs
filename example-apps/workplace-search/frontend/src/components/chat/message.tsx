import React from 'react'
import { ChatMessageType, SourceType } from 'types'
import { Loader } from 'components/loader'
import { Sources } from 'components/chat/sources'
import { ReactComponent as UserLogo } from 'images/user.svg'
import { ReactComponent as ElasticLogo } from 'images/elastic_logo.svg'
import ReactMarkdown from 'react-markdown'

type ChatMessageProps = Omit<ChatMessageType, 'id'> & {
  onSourceClick: (source: string) => void
}
export const ChatMessage: React.FC<ChatMessageProps> = ({
  content,
  isHuman,
  sources,
  loading,
  onSourceClick,
}) => {
  const messageIcon = isHuman ? (
    <span className="self-end p-2 rounded-md border border-zind-200 bg-white">
      <UserLogo className="w-6 h-6" />
    </span>
  ) : (
    <span className="self-end p-2 rounded-md bg-blue-50 shadow">
      <ElasticLogo className="w-6 h-6" />
    </span>
  )

  return (
    <div>
      <div className={`flex mt-6 gap-2 ${isHuman ? 'justify-end' : ''}`}>
        {messageIcon}

        <div
          className={`w-96 p-4 rounded-md ${
            isHuman
              ? 'rounded-br-none text-white bg-blue-500 -order-1'
              : 'bg-white shadow border-2 border-blue-100 rounded-bl-none text-zinc-700'
          }`}
        >
          <ReactMarkdown skipHtml>{content}</ReactMarkdown>
          {loading && <Loader />}
        </div>
      </div>
      {!!sources?.length && (
        <div className="mt-6 gap-2 inline-flex">
          {messageIcon}
          <Sources sources={sources || []} onSourceClick={onSourceClick} />
        </div>
      )}
    </div>
  )
}
