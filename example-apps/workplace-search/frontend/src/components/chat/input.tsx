import {
  ChangeEvent,
  FormEvent,
  KeyboardEvent,
  useLayoutEffect,
  useRef,
  useState,
} from 'react'
import autosize from 'autosize'
import { cn } from 'lib/utils'
import Conversation from 'images/conversation'
import SendIcon from 'images/send_icon'
import StopIcon from 'images/stop_icon'

export default function ChatInput({
  isMessageLoading,
  onSubmit,
  onAbortRequest,
}) {
  const [message, setMessage] = useState<string>()
  const textareaReference = useRef<HTMLTextAreaElement>(null)
  const isSubmitDisabled =
    !message || message.trim().length === 0 || isMessageLoading

  const handleSubmit = (event?: FormEvent<HTMLFormElement>) => {
    event?.preventDefault()

    if (!isSubmitDisabled) {
      onSubmit(message)

      setMessage('')
    }
  }
  const onChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    autosize(textareaReference.current)
    setMessage(event.target.value)
  }
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit()
    }
  }

  useLayoutEffect(() => {
    const ref = textareaReference?.current

    ref?.focus()
    autosize(ref)

    return () => {
      autosize.destroy(ref)
    }
  }, [])

  return (
    <form className="flex space-x-2 relative" onSubmit={handleSubmit}>
      <textarea
        className="hover:border-blue disabled:border-smoke disabled:opacity-75 w-full h-10 p-2 border border-smoke rounded-md bg-gray-50 focus:bg-white pl-9 resize-none"
        ref={textareaReference}
        value={message}
        placeholder="Ask a follow up question about this answer"
        onKeyDown={handleKeyDown}
        onChange={onChange}
        disabled={isMessageLoading}
      ></textarea>
      <span className="absolute left-1 top-3">
        <Conversation />
      </span>
      {isMessageLoading ? (
        <button
          onClick={onAbortRequest}
          className={cn(
            'hover:bg-light-ink bg-ink text-light-fog font-medium flex-row items-center justify-center w-36 px-4 py-2 rounded-md border cursor-pointer inline-flex'
          )}
        >
          <span className="mr-3">
            <StopIcon />
          </span>
          Stop
        </button>
      ) : (
        <button
          disabled={isSubmitDisabled}
          type="submit"
          className={cn(
            'enabled:hover:bg-light-ink disabled:opacity-75 bg-ink text-light-fog font-medium flex-row items-center justify-center w-36 px-4 py-2 rounded-md border disabled:cursor-not-allowed cursor-pointer inline-flex'
          )}
        >
          Send
          <span className="ml-3">
            <SendIcon />
          </span>
        </button>
      )}
    </form>
  )
}
