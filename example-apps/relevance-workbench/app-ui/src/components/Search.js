import React, { useState, useEffect } from 'react';

import SearchInput from './SearchInput';
import Results from './Results';

import Brand from './Brand';
import SettingsDropdown from './SettingsDropdown';
import IndexSelector from './IndexSelector';

export default function Search() {
  const [query, setQuery] = useState('');
  const [inputValue, setInputValue] = useState();
  const [selectedDataset, setSelectedDataset] = useState()
  const [globalSettings, setGlobalSettings] = useState({
    showMetadata: true,
    compareResults: true,

  });

  useEffect(() => {
    setQuery('')
    setInputValue('')
  }, [selectedDataset]);

  return (
    <>
      <header className="container mx-auto py-8 px-16">
        <div className="flex items-center">
          <Brand />
          <h1 className="text-lg tracking-wide text-white opacity-70">
            Relevance Workbench
          </h1>
          <SettingsDropdown globalSettings={globalSettings} setGlobalSettings={setGlobalSettings} />
        </div>
      </header>
      <SearchInput value={inputValue} setValue={setInputValue} setQuery={setQuery} />
      <IndexSelector selectedDataset={selectedDataset} setSelectedDataset={setSelectedDataset} />
      <Results query={query} globalSettings={globalSettings} selectedDataset={selectedDataset} />
    </>
  );
}