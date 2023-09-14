import { cn } from 'lib/utils'
import { AppStatus } from 'store/provider'
import ChatInput from 'components/chat/input'
import { AnswerMessage } from 'components/chat/answer_message'
import { ChatMessageList } from 'components/chat/message_list'
import { ChatMessageType, SourceType } from 'types'

interface ChatProps {
  status: AppStatus
  messages: ChatMessageType[]
  onSend: (message: string) => void
  onAbortRequest: () => void
  onSourceClick: (source: SourceType) => void
}

export const InlineChat: React.FC<ChatProps> = ({
  status,
  messages,
  onSend,
  onAbortRequest,
  onSourceClick,
}) => (
  <div className="border-t border-fog flex flex-col flex-grow overflow-hidden">
    <ChatMessageList
      className="max-h-none overflow-auto flex-grow"
      messages={messages}
      isMessageLoading={status === AppStatus.StreamingMessage}
      onSourceClick={onSourceClick}
    />
    <div className="border-t border-fog mb-6" />

    <ChatInput
      isMessageLoading={status === AppStatus.StreamingMessage}
      onSubmit={onSend}
      onAbortRequest={onAbortRequest}
    />
  </div>
)
