import { cn } from "../../lib/utils";
import { useEffect, useState } from "react";
import { Reload } from "../images/reload";
import SearchIcon from "../images/searchIcon";

export default function SearchInput({ onSearch, searchActive, value }) {
  const [query, setQuery] = useState<string>(value);

  useEffect(() => {
    setQuery(value);
  }, [value]);
  return (
    <form
      className="w-full"
      onSubmit={(e) => {
        e.preventDefault();
        if (query.length === 0) return;
        onSearch(query);
      }}
    >
      <label className="text-xs font-bold leading-none text-gray-900">
        Search everything
      </label>
      <div className="relative mt-1 flex w-full items-center space-x-2">
        <input
          type="text"
          className="w-full rounded-md border border-light-smoke px-3 py-2.5 pl-10 text-base font-medium outline-none placeholder-gray-400 focus:border-transparent focus:ring-2 focus:ring-blue-500"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ask your question here"
        />
        <span className="pointer-events-none absolute left-2">
          <SearchIcon />
        </span>
        <button
          className={cn(
            "flex flex-row bg-dark-blue text-light-fog py-2.5 w-48 rounded-md font-medium items-center justify-center"
          )}
          type="submit"
        >
          {searchActive && (
            <span className="mr-2">
              <Reload />
            </span>
          )}{" "}
          {searchActive ? "Start over" : "Search"}
        </button>
      </div>
    </form>
  );
}
