import { cn } from 'lib/utils'
import { AppStatus } from 'store/provider'
import ChatInput from 'components/chat/input'
import { AnswerMessage } from 'components/chat/answer_message'
import { ChatMessageList } from 'components/chat/message_list'
import { ChatMessageType } from 'types'

interface ChatProps {
  status: AppStatus
  messages: ChatMessageType[]
  summary: ChatMessageType
  onSend: (message: string) => void
  onAbortRequest: () => void
  onSourceClick: (sourceName: string) => void
}

export const Chat: React.FC<ChatProps> = ({
  status,
  messages,
  summary,
  onSend,
  onAbortRequest,
  onSourceClick,
}) => (
  <div className="rounded-md shadow bg-white mt-6 p-6 border border-light-fog mb-8">
    <div className="mb-4">
      <AnswerMessage
        text={summary?.content}
        sources={summary?.sources || []}
        onSourceClick={onSourceClick}
      />
    </div>

    <div
      className={cn('border-t border-fog', {
        'border-0': messages.length === 0,
      })}
    >
      {!!messages.length && (
        <>
          <ChatMessageList
            messages={messages}
            isMessageLoading={status === AppStatus.StreamingMessage}
            onSourceClick={onSourceClick}
          />
          <div className="border-t border-fog mb-6" />
        </>
      )}

      <ChatInput
        isMessageLoading={status === AppStatus.StreamingMessage}
        onSubmit={onSend}
        onAbortRequest={onAbortRequest}
      />
    </div>
  </div>
)
