import React from "react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  content: string;
  dataSource: string;
  created: string;
  link?: string;
  source?: Record<string, any>;
}

export const SearchResultModal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  content,
  dataSource,
  created,
  link,
  source,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50"
      aria-modal="true"
      role="dialog"
      aria-label="A modal with the full details of the selected document"
    >
      <div
        className="absolute inset-0 bg-black opacity-50"
        onClick={onClose}
      ></div>
      <div className="relative bg-white p-8 rounded-lg w-11/12 md:w-3/4 lg:w-1/2 shadow-xl">
        <button
          aria-label="Close modal"
          className="absolute top-2 right-2 text-gray-600 hover:text-gray-900"
          onClick={onClose}
        >
          X
        </button>

        <div className="mb-6">
          <h2 className="mb-4 text-2xl font-bold">{title}</h2>
          <p>
            <strong>Data Source:</strong> {dataSource}
          </p>
          <p>
            <strong>Created:</strong> {created}
          </p>
          {link && link !== "Unknown" && (
            <p>
              <strong>Link:</strong>{" "}
              <a
                href={link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {link}
              </a>
            </p>
          )}
        </div>

        <p className="text-gray-700 text-left mb-6">{content}</p>
        <div className="mb-6">
          {source ? (
            <>
              <p className="mb-6">
                <strong>Full document source:</strong>
              </p>
              <pre className="max-h-96 overflow-scroll">
                <code>{JSON.stringify(source, undefined, 2)}</code>
              </pre>
            </>
          ) : (
            <></>
          )}
        </div>
      </div>
    </div>
  );
};
