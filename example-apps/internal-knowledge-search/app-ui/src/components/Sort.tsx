import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { setSortOrder } from "../store/slices/sortSlice";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowUp, faArrowDown } from "@fortawesome/free-solid-svg-icons";
import { RootState } from "../store/store";

interface SortProps {
  sortKey: string;
}

export const Sort: React.FC<SortProps> = ({ sortKey }) => {
  const dispatch = useDispatch();
  const { title, sortDirection } = useSelector(
    (state: RootState) => state.sort.sorts[sortKey]
  );

  const toggleSortOrder = () => {
    const newSortDirection = sortDirection === "asc" ? "desc" : "asc";
    dispatch(setSortOrder({ key: sortKey, sortDirection: newSortDirection }));
  };

  return (
    <button
      onClick={toggleSortOrder}
      className="bg-blue-600 text-white py-2 px-4 rounded-lg shadow-md hover:bg-blue-700 active:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-all duration-200"
    >
      {title}:
      <span className="ml-2">
        {sortDirection === "asc" ? (
          <FontAwesomeIcon icon={faArrowUp} />
        ) : (
          <FontAwesomeIcon icon={faArrowDown} />
        )}
      </span>
    </button>
  );
};
