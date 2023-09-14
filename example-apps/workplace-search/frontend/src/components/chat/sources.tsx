import { SourceItem } from '../source_item'
import { SourceType } from 'types'

export type SourcesProps = {
  sources: SourceType[]
  showDisclaimer?: boolean
  onSourceClick: (source: SourceType) => void
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

        <div className="relative inline-flex">
          <div className="overflow-auto scroll-smooth no-scrollbar">
            <div className="inline-flex gap-2">
              {sources.map((source) => (
                <SourceItem
                  key={source.name}
                  {...source}
                  onSourceClick={onSourceClick}
                />
              ))}
            </div>
          </div>
          <span className="absolute right-0 h-full w-6 bg-gradient-to-r from-transparent to-white" />
        </div>
      </>
    )) ||
    null
  )
}
