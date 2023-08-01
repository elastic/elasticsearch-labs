import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { debounce } from 'lodash';
import classNames from 'classnames';

import { MagnifyingGlassIcon } from "@heroicons/react/24/solid";

export default function SearchInput({ value, setValue, setQuery }) {
  const [isFocused, setIsFocused] = useState(false);
  

  const useDebounce = (callback) => {
    const ref = useRef();
  
    useEffect(() => {
      ref.current = callback;
    }, [callback]);
  
    const debouncedCallback = useMemo(() => {
      const func = () => {
        ref.current?.();
      };
  
      return debounce(func, 1000);
    }, []);
  
    return debouncedCallback;
  };
  

  // Handle focus
  const handleFocus = () => {
    setIsFocused(true);
  };

  // Handle blur
  const handleBlur = () => {
    setIsFocused(false);
  };

  // Focus input when container is clicked
  const handleClick = () => {
    !isFocused && document.getElementById('search_input').focus();
  };

  const handleChange = (e) => {
    const value = e.target.value;
    setValue(value);

    debouncedRequest();
  };

  useEffect(() => {
    // Focus input when page loads
    document.getElementById('search_input').focus();
  }, []);

  const debouncedRequest = useDebounce(() => {
    // send request to the backend
    // access to latest state here
    console.log(value);
    setQuery(value);
  });

  const searchClasses = classNames(
    "w-full flex items-center font-bold text-2xl tracking-wide rounded-full relative transition-all duration-75 ease-in-out cursor-text",
    {
      "bg-[rgba(255,255,255,1)] text-slate-800": isFocused,
      "bg-[rgba(255,255,255,0.1)] text-white": !isFocused,
    }
  );

  return (
    <div className="container mx-auto px-24">
      <div
        className={searchClasses}
        onClick={handleClick}
        onBlur={handleBlur}
        onFocus={handleFocus}
      >
        <MagnifyingGlassIcon className="h-10 w-10 text-elastic-blue-lighter opacity-70 absolute left-8 top-1/2 transform -translate-y-1/2 pointer-events-none" />
        <input
          id="search_input"
          type="text"
          className="w-full appearance-none bg-transparent border-none text-inherit font-bold text-2xl pl-20 pr-8 h-24 focus:outline-none"
          placeholder="Enter a query..."
          value={value}
          onChange={handleChange}
        />
      </div>
    </div>
  );
}