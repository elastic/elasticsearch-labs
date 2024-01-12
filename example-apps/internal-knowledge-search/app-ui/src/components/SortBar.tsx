import React from "react";
import { Sort } from "./Sort";
import { useSelector } from "react-redux";
import { RootState } from "../store/store";

export const SortBar: React.FC = () => {
  const sorts = useSelector((state: RootState) => state.sort.sorts);

  return (
    <div className="bg-gray-100 p-4 rounded-lg shadow-md">
      {Object.keys(sorts).map((sort) => (
        <Sort key={sort} sortKey={sort} />
      ))}
    </div>
  );
};
