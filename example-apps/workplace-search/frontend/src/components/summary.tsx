import { SourceType } from "./source_item";
import { Sources } from "./sources";

export const Summary = ({
  text,
  sources,
}: {
  text: string | undefined;
  sources: SourceType[];
}) => {
  return (
    <div className="mb-4">
      <header className="flex flex-row justify-between mb-8">
        <div className="flex flex-row justify-center align-middle items-center">
          <div className="flex flex-col justify-start">
            <h2 className="text-xl font-bold">Answer</h2>
            <p className="text-sm font-medium text-dark-smoke">
              Powered by Elasticsearch with Azure OpenAI
            </p>
          </div>
        </div>
      </header>
      {isLoading && !text && (
        <div className="ml-4">
          <BeatLoader size={7}/>
        </div>
      )}
      {text && (
        <div className="text-base leading-tight text-gray-800 whitespace-pre-wrap mb-8">
          {text}
        </div>
      )}
      {/*<Sources showDisclaimer sources={sources} />*/}
    </div>
  );
};
