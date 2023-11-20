import React from 'react'
import { SourceIcon } from './source_icon'

export type SourceProps = {
  name: string
  icon: string
  onSourceClick: (sourceName: string) => void
}

export const SourceItem: React.FC<SourceProps> = ({
  name,
  icon,
  onSourceClick,
}) => (
  <div
    onClick={() => {
      onSourceClick(name)
    }}
    className="hover:text-blue-600 hover:border-blue-500 inline-flex gap-2 items-center cursor-pointer px-4 py-3 border-2 rounded-md border-blue-300 text-blue-500 font-medium"
  >
    <SourceIcon icon={icon} />
    <span>{name}</span>
  </div>
)
