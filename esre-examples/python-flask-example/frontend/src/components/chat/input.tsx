import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import autosize from "autosize";
import { cn } from "../../lib/utils";
import Conversation from "../images/conversation";
import SendIcon from "../images/SendIcon";

export default function ChatInput({ isLoading, onSubmit }) {
  const [message, setMessage] = useState<string>();
  const textareaReference = useRef<HTMLTextAreaElement>(null);

  const sendMessage = useCallback(() => {
    if (message && message.trim().length > 0) {
      onSubmit(message);
      setMessage("");
      autosize.destroy(textareaReference.current);
    }
  }, [message, onSubmit]);

  const handleKeyDown = useCallback(
    (event) => {
      if (
        event.keyCode === 13 &&
        !event.shiftKey &&
        message &&
        message.trim().length > 0
      ) {
        event.preventDefault();

        sendMessage();
      }
    },
    [message, sendMessage]
  );


  const handleSubmit = useCallback((event) => {
    event.preventDefault();
  }, []);

  useEffect(() => {
    const ref = textareaReference?.current;

    if (!isLoading && ref) {
      ref.focus();
    }
  }, [isLoading]);

  useLayoutEffect(() => {
    const ref = textareaReference?.current;

    autosize(ref);

    return () => {
      autosize.destroy(ref);
    };
  }, []);

  return (
    <form className="flex space-x-2 relative" onSubmit={handleSubmit}>
      <textarea
        className="w-full h-10 p-2 border border-smoke rounded-md bg-gray-50 focus:bg-white pl-9 resize-none"
        ref={textareaReference}
        value={message}
        placeholder="Ask a follow up question about this answer"
        onKeyDown={handleKeyDown}
        onChange={(event) => {
          autosize(textareaReference.current);
          setMessage(event.target.value);
        }}
      ></textarea>
      <span className="absolute left-1 top-3">
        <Conversation />
      </span>
      <button
        disabled={!message || message?.length === 0}
        onClick={sendMessage}
        type="submit"
        className={cn(
          "bg-ink text-light-fog font-medium flex-row items-center justify-center w-36 px-4 py-2 rounded-md border disabled:opacity-100 disabled:cursor-not-allowed cursor-pointer inline-flex"
        )}
      >
        Send{" "}
        <span className="ml-3">
          <SendIcon />
        </span>
      </button>
    </form>
  );
}
