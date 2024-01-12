import React, { ChangeEvent, useEffect, useState } from "react";
import { FaMagnifyingGlass } from "react-icons/fa6";

interface SearchBarProps {
  value: string;
  onSubmit: () => void;
  onQueryChange: (value: string) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onSubmit,
  onQueryChange,
}) => {
  const [query, setQuery] = useState<string>(value);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
    onQueryChange(event.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  useEffect(() => {
    setQuery(value);
  }, [value]);

  return (
    <form onSubmit={handleSubmit}>
      <div className="flex justify-center items-center">
        <div className="relative w-3/5">
          <span className="absolute left-4 text-gray-400 top-1/2 transform -translate-y-1/2">
            <FaMagnifyingGlass />
          </span>
          <input
            type="text"
            placeholder="Search..."
            value={query}
            onChange={handleChange}
            className="w-full p-4 pl-10 text-lg bg-white border border-gray-300 rounded-full focus:outline-none focus:shadow-outline"
          />
        </div>
      </div>
    </form>
  );
};
