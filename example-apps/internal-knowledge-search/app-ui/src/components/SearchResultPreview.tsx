import React, { useState } from "react";
import { SearchResultModal } from "./SearchResultModal";
import { SearchResultModel } from "../models/SearchResultModel";

export const SearchResultPreview: React.FC<SearchResultModel> = ({
  title,
  created,
  dataSource,
  dataSourceImagePath,
  previewText,
  fullText,
  link,
  source,
}) => {
  const [isModalOpen, setModalOpen] = useState<boolean>(false);

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200">
      <div className="mb-4 border-b pb-4 border-gray-200">
        <h2 className="text-xl font-bold">{title}</h2>
      </div>
      <div className="flex justify-between items-center mb-4">
        <div className="text-sm text-gray-500">
          <span className="font-bold">Created:</span>{" "}
          {new Date(created).toLocaleDateString()}
        </div>
        <span className="flex items-center text-gray-800 border border-gray-400 px-3 py-1 text-xs rounded font-semibold">
          {dataSourceImagePath && (
            <>
              <img
                src={dataSourceImagePath}
                alt="Description"
                className="w-4 h-4 mr-2"
              />
              <span className="border-l border-gray-800 mx-2 h-4"></span>
            </>
          )}
          <span>Source index: {dataSource}</span>
        </span>
      </div>
      <div className="text-gray-600 border-t pt-4 border-gray-200 mt-2 mb-4">
        {previewText}
      </div>
      <div className="flex justify-end space-x-4 mt-4">
        {link && link !== "Unknown" && (
          <button
            onClick={() => window.open(link, "_blank")}
            className="text-blue-600 border border-blue-600 bg-white px-3 py-1 rounded hover:bg-blue-100 transition-colors duration-200 text-sm"
          >
            View Original Source
          </button>
        )}
        <button
          className="text-white bg-blue-600 px-3 py-1 rounded hover:bg-blue-700 transition-colors duration-200 text-sm"
          onClick={() => setModalOpen(true)}
        >
          Read Full Document
        </button>
      </div>

      <SearchResultModal
        isOpen={isModalOpen}
        onClose={() => setModalOpen(false)}
        title={title}
        content={fullText}
        link={link}
        dataSource={dataSource}
        created={created}
        source={source}
      />
    </div>
  );
};
