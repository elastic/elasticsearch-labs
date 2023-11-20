import React, { Fragment } from 'react'
import { ReactComponent as LightBulb } from 'images/light_bulb_icon.svg'
import { SourceType } from '../types'
import { SourceIcon } from './source_icon'
import { SearchResult } from './search_result'

interface SearchResultsProps {
  results: SourceType[]
  toggleSource: (source: string) => void
}

export const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  toggleSource,
}) =>
  !!results?.length ? (
    <>
      <h2 className="text-zinc-400 text-sm font-medium mb-3 inline-flex items-center gap-2">
        <LightBulb /> Search results
      </h2>
      <div className="flex gap-y-4 flex-col">
        {results?.map((result) => (
          <SearchResult
            key={result.name}
            toggleSource={toggleSource}
            {...result}
          />
        ))}
      </div>
    </>
  ) : null
