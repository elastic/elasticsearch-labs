import React from 'react'
import { SourceIcon } from './source_icon'
import { SourceType } from '../types'

export type SourceProps = SourceType & {
  onSourceClick: (source: SourceType) => void
}

export const SourceItem: React.FC<SourceProps> = ({
  name,
  summary,
  url,
  icon,
  onSourceClick,
}) => (
  <div
    onClick={() => {
      onSourceClick({ name, url, icon, summary } as SourceType)
    }}
    className="hover:text-blue-600 hover:border-blue-500 flex-shrink-0 inline-flex gap-2 items-center cursor-pointer px-4 py-3 border-2 rounded-md border-blue-300 text-blue-500 font-medium"
  >
    <SourceIcon icon={icon} />
    <span>{name}</span>
  </div>
)
