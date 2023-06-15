import { useEffect, useRef, useState } from "react";
import { ChatMessageType, ChatMessage } from "./chat_message";

type ChatMessageListType = {
  messages: ChatMessageType[];
  incomingMessage: string | null;
};
export const ChatMessageList: React.FC<ChatMessageListType> = ({
  messages,
  incomingMessage,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [userScrolled, setUserScrolled] = useState(false);


  useEffect(() => {
    const container = containerRef.current;
    // Scroll to bottom when new messages come in and the user hasn't scrolled up
    if (container && !userScrolled) {
      container.scrollTop = container.scrollHeight;
    }
  }, [incomingMessage, messages, userScrolled]);

  const handleScroll = () => {
    const container = containerRef.current;
    // Check if the user has scrolled up
    if (container) {
      const { scrollTop, clientHeight, scrollHeight } = container;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight;
      setUserScrolled(!isAtBottom);
    }
  };

  return (
    <div className="w-full mb-8 overflow-y-scroll max-h-96 pb-5 px-5 overflow-x-visible" ref={containerRef} onScroll={handleScroll}>
      {messages.map((msg) => (
        <ChatMessage
          key={msg.id}
          id={msg.id}
          content={msg.content}
          isHuman={msg.isHuman}
          sources={msg.sources || undefined}
        />
      ))}

      {incomingMessage && messages.length > 0 && (
        <ChatMessage
          key={messages.length + 1}
          id={messages.length + 1}
          content={incomingMessage}
          isHuman={false}
        />
      )}
    </div>
  );
};
