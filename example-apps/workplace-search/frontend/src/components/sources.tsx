import { SourceItem } from './source_item'

export type SourcesProps = {
  sources: string[]
  showDisclaimer?: boolean
}
export const Sources: React.FC<SourcesProps> = ({
  sources,
  showDisclaimer,
}) => {
  return (
    (sources.length > 0 && (
      <>
        {showDisclaimer && (
          <h5 className="text-xs font-medium tracking-normal leading-normal uppercase text-lighter-ink mb-3">
            The answer was formed from
            <br />
            information found in this document
          </h5>
        )}
        <div className="flex space-x-2 flex-wrap">
          {sources.map((source) => (
            <SourceItem
              key={source}
              name={source}
              // icon={source.icon}
              // url={source.url}
            />
          ))}
        </div>
      </>
    )) ||
    null
  )
}
