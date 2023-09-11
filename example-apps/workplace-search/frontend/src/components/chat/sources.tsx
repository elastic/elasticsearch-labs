import { SourceItem } from '../source_item'
import { SourceType } from 'types'

export type SourcesProps = {
  sources: SourceType[]
  showDisclaimer?: boolean
  onSourceClick: (source: string) => void
}
export const Sources: React.FC<SourcesProps> = ({
  sources,
  showDisclaimer,
  onSourceClick,
}) => {
  return (
    (sources.length > 0 && (
      <>
        {showDisclaimer && (
          <h5 className="text-zinc-400 text-sm mb-2">Sourced from</h5>
        )}

        <div className="flex space-x-2 flex-wrap">
          {sources.map((source) => (
            <SourceItem
              key={source.name}
              name={source.name}
              icon={source.icon}
              onSourceClick={onSourceClick}
            />
          ))}
        </div>
      </>
    )) ||
    null
  )
}
