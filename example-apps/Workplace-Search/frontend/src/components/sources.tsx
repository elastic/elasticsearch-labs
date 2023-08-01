import { SourceItem, SourceType } from "./source_item";

export type SourcesType = {
  sources: SourceType[];
  showDisclaimer?: boolean;
};
export const Sources: React.FC<SourcesType> = ({ sources, showDisclaimer }) => {
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
              key={source.name}
              name={source.name}
              icon={source.icon}
              href={source.href}
            />
          ))}
        </div>
      </>
    )) ||
    null
  );
};
