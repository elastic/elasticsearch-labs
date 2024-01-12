import React from "react";
import { SearchResultPreview } from "./SearchResultPreview";
import { useSelector } from "react-redux";
import { RootState } from "../store/store";

export const SearchResults: React.FC = () => {
  const { results } = useSelector((state: RootState) => state.searchResults);

  return (
    <div className="w-full max-w-2xl bg-white p-4 rounded-lg shadow-md">
      {results.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12">
          <span className="text-lg font-medium text-gray-500 mb-4">
            No results
          </span>
        </div>
      ) : (
        <div className="space-y-4">
          {results.map((result, index) => (
            <SearchResultPreview
              key={index}
              title={result.title}
              created={result.created}
              dataSource={result.dataSource}
              dataSourceImagePath={result.dataSourceImagePath}
              previewText={result.previewText}
              fullText={result.fullText}
              link={result.link}
              source={result.source}
            />
          ))}
        </div>
      )}
    </div>
  );
};
