'use client';

import Image from 'next/image';
import SearchBar from './SearchBar';

export default function SiteHeader({
  value,
  onChange,
  onSearch,
  onRandom,
  onPreviousPage,
  onNextPage,
  isLoading,
  canPaginate,
  isFirstPage,
  isLastPage,
}) {
  return (
    <header className="sa-header">
      <div className="sa-header__top">
        <a
          href="https://searchali.com"
          className="sa-header__brand"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="searchali.com"
        >
          <Image
            src="/icons/logo.png"
            alt="searchali.com"
            width={519}
            height={112}
            className="sa-header__brand-logo"
            priority
          />
        </a>

        <h1 className="sa-header__title">Elasticsearch Query Comparer</h1>

        <div className="sa-header__partner">
          <Image
            src="/icons/elastic-partner-banner.webp"
            alt="Elastic Partner"
            width={1000}
            height={1000}
            className="sa-header__partner-logo"
          />
        </div>
      </div>

      <div className="sa-header__toolbar">
        <SearchBar
          value={value}
          onChange={onChange}
          onSearch={onSearch}
          onRandom={onRandom}
          onPreviousPage={onPreviousPage}
          onNextPage={onNextPage}
          isLoading={isLoading}
          canPaginate={canPaginate}
          isFirstPage={isFirstPage}
          isLastPage={isLastPage}
        />
      </div>
    </header>
  );
}
