import React from "react";
import { createContext, ReactNode, useContext, useState } from "react";
import { MessageType, Toast } from "../components/Toast";

interface ToastContextType {
  showToast: (message: string, type?: MessageType) => void;
}

interface Message {
  text: string;
  type: MessageType;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};

export const ToastProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [message, setMessage] = useState<Message>({
    text: "",
    type: MessageType.Info,
  });
  const [visible, setVisible] = useState(false);

  const showToast = (msg: string, type: MessageType = MessageType.Info) => {
    const afterThreeSeconds = 3000;

    setMessage({ text: msg, type });
    setVisible(true);
    setTimeout(() => setVisible(false), afterThreeSeconds);
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {visible && <Toast text={message.text} type={message.type} />}
    </ToastContext.Provider>
  );
};
