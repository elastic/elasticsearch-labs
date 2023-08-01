import { useState, useEffect } from 'react';

import ResultSet from './ResultSet';

export default function Results({ query, globalSettings, selectedDataset }) {
  const [results, setResults] = useState([]);
  const [enableRrf, setEnableRrf] = useState(true);
  const [activeResult, setActiveResult] = useState(null);

  const types = [
    {
      id: 'elser',
      label: 'Elastic Learned Sparse Encoder',
      rrf_capable: true,
      theme: "light",
      showChange: true
    }, {
      id: 'bm25',
      label: 'BM25',
      showChange: false,
      theme: "dark",
      rrf_capable: false
    }
  ]

  useEffect(() => {
    console.log(enableRrf)
    if (query) {
      setResults([])
      types.forEach((type) => {
        fetch(`api/search/${selectedDataset.index}?q=${query}&rrf=${enableRrf}&type=${type.id}&dataset=${selectedDataset.id}`)
          .then((res) => res.json())
          .then((data) => {
            setResults((results) => {
              return {
                ...results,
                [type.id]: data.response,
              }
            });
          });
      });
    } else {
      setResults([])
    }
  }, [query, enableRrf]);

  useEffect(() => {
    if (results['bm25'] && results['elser']) {
      console.log()
      console.log("Comparing results...")
      const firstResultSet = results['elser'];
      const secondResultSet = results['bm25'];

      firstResultSet.forEach((result, index) => {
        // Find the same result in the second result set
        const secondResult = secondResultSet.find((secondResult) => {
          return secondResult._id === result._id;
        });

        // If the result is not found in the second result set, log it
        if (secondResult) {
          const secondIndex = secondResultSet.indexOf(secondResult);
          result.change = secondIndex - index;
        } else {
          result.change = null
        }
      });
    }

    
  }, [results, enableRrf]);


  return (
    <div className="container mx-auto py-12">
      <div className="grid grid-cols-2 gap-8">
        {query && results && Object.keys(results).length == 2 &&
          types.map((type) => (
            <ResultSet
              key={type.id}
              index={selectedDataset.index}
              type={type}
              query={query}
              results={results[type.id] || []}
              enableRrf={enableRrf}
              setEnableRrf={setEnableRrf}
              activeResult={activeResult}
              setActiveResult={setActiveResult}
              globalSettings={globalSettings}
            />
          ))
        }
      </div>
    </div>
  );
}