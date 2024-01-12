import React from "react";
import { Filter } from "./Filter";
import { useSelector } from "react-redux";
import { RootState } from "../store/store";

export const FilterBar: React.FC = () => {
  const filters = useSelector((state: RootState) => state.filter)["filters"];

  return (
    <div className="bg-gray-100 p-4 rounded border border-gray-300 my-4 flex space-x-4">
      {Object.keys(filters).map((filter) => (
        <Filter key={filter} label={filter} />
      ))}
    </div>
  );
};
