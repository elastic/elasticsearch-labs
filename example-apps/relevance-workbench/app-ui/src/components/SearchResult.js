import { useState, useEffect, useLayoutEffect, useRef } from "react";
import classNames from "classnames";
import PropTypes from "prop-types";


const useTruncatedElement = ({ ref }) => {
  const [isTruncated, setIsTruncated] = useState(false);
  const [isShowingMore, setIsShowingMore] = useState(false);

  useLayoutEffect(() => {
    const { offsetHeight, scrollHeight } = ref.current || {};

    if (offsetHeight && scrollHeight && offsetHeight < scrollHeight) {
      setIsTruncated(true);
    } else {
      setIsTruncated(false);
    }
  }, [ref]);

  const toggleIsShowingMore = () => setIsShowingMore(prev => !prev);

  return {
    isTruncated,
    isShowingMore,
    toggleIsShowingMore,
  };
};

export default function SearchResult({ result, theme, activeResult, setActiveResult, globalSettings, showChange }) {
  const [isDiminished, setIsDiminished] = useState(false);
  const [isEmphasized, setIsEmphasized] = useState(false);
  const { _id, _score, change, fields } = result;

  const { title, text } = fields;

  const ref = useRef(null);
  const { isTruncated, isShowingMore, toggleIsShowingMore } = useTruncatedElement({
    ref,
  });

  const resultClasses = classNames(
    `flex flex-col mb-4 rounded px-6 py-4 result-${_id}`,
    {
      "bg-white": theme === "light",
      "opacity-50": isDiminished && globalSettings.compareResults,
      "bg-[rgba(255,255,255,0.1)]": theme === "dark",
      "bg-[rgba(255,255,255,0.25)]": theme === "dark" && isEmphasized && globalSettings.compareResults,
    }
  );

  // Handle hover state
  const handleMouseEnter = () => {
    setActiveResult(_id);
  };

  const handleMouseLeave = () => {
    setActiveResult(null);
  };

  useEffect(() => {
    if (activeResult) {

      if (activeResult === _id) {
        setIsDiminished(false);
        setIsEmphasized(true);
      } else {
        setIsDiminished(true);
        setIsEmphasized(false);
      }
    } else {
      setIsDiminished(false);
      setIsEmphasized(false);
    }
  }, [_id, activeResult]);

  const changeClasses = classNames("font-bold", {
    "text-green-500": change > 0,
    "text-red-500": change < 0,
    "font-sans bg-yellow-300 px-1 rounded-sm text-black": !change
  });

  return (
    <div 
      className={resultClasses} 
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {globalSettings.showMetadata && (
        <div className={`flex items-center justify-between text-sm font-mono font-medium mb-2 ${
            theme == "dark" ? "text-white opacity-75" : "text-slate-400"
          }`}>
          <span>
            Score: {_score? _score: "N/A"}
          </span>
          {showChange && <span className={changeClasses}>
            {change > 0 && '+'}
            {(change == null) ? 'New': (change != 0)? change: ""}
          </span>}
        </div>
      )}
      <h3
        className={`text-xl font-bold mb-2 whitespace-nowrap text-ellipsis overflow-hidden ${
          theme == "dark" && "text-white"
        }`}
      >
        {title}
      </h3>
      <p ref={ref} className={`text-sm h-16 min-h-[4rem] ${!isShowingMore && 'line-clamp-3'} ${isShowingMore && 'h-auto'} ${
          theme == "dark" && "text-white"
        }`}>
        {text}
      </p>
      {/* {isTruncated && ( */}
        <button className={`${
          theme == "dark" && "text-white"
        }`} onClick={toggleIsShowingMore}>
          {isShowingMore ? <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="m-auto w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
</svg>
 : <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="m-auto w-6 h-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
</svg>
}
        </button>
      {/* )} */}
    </div>
  );
}

SearchResult.propTypes = {
  result: PropTypes.object.isRequired,
  theme: PropTypes.string.isRequired,
};