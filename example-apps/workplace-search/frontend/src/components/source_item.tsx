import React from 'react'

import { SourceIcon, SourceIconType } from './source_icon'

export type SourceType = {
  name: string
  summary?: string[]
  url?: string
}

export const SourceItem: React.FC<SourceType> = ({ name, url }) => {
  const styles = {
    wrapper: {
      background: 'linear-gradient(180deg, #F7F9FC 0%, #F1F4FA 100%)',
      padding: '8px 12px 8px 8px',
      height: '40px',
      boxShadow:
        '0px 0.7px 3.4px rgba(0, 0, 0, 0.15), 0px 1.9px 8px rgba(0, 0, 0, 0.03), 0px 4.5px 16px rgba(0, 0, 0, 0.1), inset 0px 1px 1px #FFFFFF',
      borderRadius: '12px',
    },
    label: {
      color: 'hsla(205, 100%, 38%, 1)',
      fontFamily: 'Inter',
      fontStyle: 'normal',
      fontWeight: 700,
      fontSize: '14px',
      lineHeight: '20px',
      textShadow: '0px -1px 0px #FFFFFF',
      flex: 'none',
      order: 1,
      flexGrow: 0,
    },
  }
  return (
    <div className="sourceItem flex-wrap flex-none" style={styles.wrapper}>
      <a
        href={url}
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center gap-2 truncate"
      >
        {/*<SourceIcon icon={icon} />*/}
        <span style={styles.label}>{name}</span>
      </a>
    </div>
  )
}
