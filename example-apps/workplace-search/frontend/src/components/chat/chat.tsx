import { cn } from 'lib/utils'
import { AppStatus } from 'store/provider'
import ChatInput from 'components/chat/input'
import { Summary } from 'components/summary'
import { ChatMessageList } from 'components/chat/message_list'

export const Chat = ({ status, messages, summary, onSend, onAbortRequest }) => (
  <div className="bg-white shadow-xl mt-4 p-6 rounded-xl border border-light-fog mb-8">
    <div className="mb-4">
      <Summary text={summary?.content} sources={summary?.sources || []} />
    </div>

    <div
      className={cn('chat border-t border-fog', {
        'border-0': messages.length === 0,
      })}
    >
      {!!messages.length && (
        <div className="chat__messages">
          <ChatMessageList
            messages={messages}
            isMessageLoading={status === AppStatus.StreamingMessage}
          />
        </div>
      )}

      <ChatInput
        isMessageLoading={status === AppStatus.StreamingMessage}
        onSubmit={onSend}
        onAbortRequest={onAbortRequest}
      />
    </div>
  </div>
)
