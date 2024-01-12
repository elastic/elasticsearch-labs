import React from "react";

export enum MessageType {
  Info,
  Warning,
  Error,
}

interface ToastProps {
  text: string;
  type: MessageType;
}

export const Toast: React.FC<ToastProps> = ({ text, type }) => {
  const getColor = (messageType: MessageType) => {
    switch (messageType) {
      case MessageType.Info:
        return "bg-blue-500";
      case MessageType.Warning:
        return "bg-yellow-500";
      case MessageType.Error:
        return "bg-red-600";
    }
  };

  return (
    <div
      className={`fixed bottom-0 right-0 m-4 p-4 text-white rounded-lg shadow-lg transform transition-transform duration-500
                        ${getColor(type)} ${!text ? "translate-y-full" : ""}`}
    >
      {text}
    </div>
  );
};
