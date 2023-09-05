import { useCallback, useLayoutEffect, useRef, useState } from 'react'
import autosize from 'autosize'
import { cn } from '../../lib/utils'
import Conversation from '../images/conversation'
import SendIcon from '../images/send_icon'
import StopIcon from '../images/stop_icon'

export default function ChatInput({
  isMessageLoading,
  onSubmit,
  onAbortRequest,
}) {
  const [message, setMessage] = useState<string>()
  const [abortRequest, setAbortRequest] = useState<() => void>()
  const textareaReference = useRef<HTMLTextAreaElement>(null)

  const onChange = useCallback((event) => {
    autosize(textareaReference.current)
    setMessage(event.target.value)
  }, [])
  const sendMessage = useCallback(() => {
    if (message && message.trim().length > 0) {
      const controller = new AbortController()

      setAbortRequest(() => () => {
        console.log('aborting', !!controller?.abort)
        controller?.abort('stop request')

        onAbortRequest?.()
      })
      onSubmit(message, controller.signal)

      setMessage('')
    }
  }, [message, onSubmit])
  const handleKeyDown = useCallback(
    (event) => {
      if (event.keyCode === 13 && !event.shiftKey) {
        event.preventDefault()

        sendMessage()
      }
    },
    [message, sendMessage]
  )
  const handleSubmit = useCallback((event) => {
    event.preventDefault()
  }, [])

  useLayoutEffect(() => {
    const ref = textareaReference?.current

    autosize(ref)

    if (ref) {
      ref.focus()
    }

    return () => {
      autosize.destroy(ref)
    }
  }, [])

  return (
    <form className="flex space-x-2 relative" onSubmit={handleSubmit}>
      <textarea
        className="hover:border-blue disabled:opacity-75 w-full h-10 p-2 border border-smoke rounded-md bg-gray-50 focus:bg-white pl-9 resize-none"
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
      {isMessageLoading && abortRequest ? (
        <button
          onClick={abortRequest}
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
          disabled={!message || message?.length === 0 || isMessageLoading}
          onClick={sendMessage}
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
