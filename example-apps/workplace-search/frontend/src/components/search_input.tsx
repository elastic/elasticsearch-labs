import { ChangeEvent, FormEvent, useEffect, useState } from 'react'
import { cn } from 'lib/utils'
import { Reload } from 'images/reload'
import SearchIcon from 'images/search_icon'
import { AppStatus } from 'store/provider'

export default function SearchInput({ onSearch, value, appStatus }) {
  const [query, setQuery] = useState<string>(value)
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (!!query.length) {
      onSearch(query)
    }
  }
  const handleChange = (event: ChangeEvent<HTMLInputElement>) =>
    setQuery(event.target.value)

  useEffect(() => {
    setQuery(value)
  }, [value])

  return (
    <form className="w-full" onSubmit={handleSubmit}>
      <label className="text-xs font-bold leading-none text-gray-900">
        Search everything
      </label>
      <div className="relative mt-1 flex w-full items-center space-x-2">
        <input
          type="text"
          className="hover:border-blue w-full rounded-md border border-light-smoke px-3 py-2.5 pl-10 text-base font-medium placeholder-gray-400"
          value={query}
          onChange={handleChange}
          placeholder="Ask your question here"
        />
        <span className="pointer-events-none absolute left-2">
          <SearchIcon />
        </span>
        <button
          disabled={appStatus === AppStatus.StreamingMessage}
          className={cn(
            'hover:bg-blue flex flex-row bg-dark-blue text-light-fog py-2.5 w-48 rounded-md font-medium items-center justify-center'
          )}
          type="submit"
        >
          {appStatus === AppStatus.Idle ? (
            'Search'
          ) : (
            <>
              <span className="mr-2">
                <Reload />
              </span>
              Start over
            </>
          )}
        </button>
      </div>
    </form>
  )
}
