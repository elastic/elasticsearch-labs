import { Avatar } from "./avatar";
import { FeedbackControl } from "./FeedbackControl/feedback_control";
import { BeatLoader } from "react-spinners";
import { SourceItem, SourceType } from "./source_item";
import { Result } from "../types";
import { Sources } from "./sources";

export const Summary = ({
  text,
  loading,
  sources,
}: {
  text: string | undefined;
  loading: boolean;
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
          {loading && (
            <div className="ml-4">
              <BeatLoader size={7} />
            </div>
          )}
        </div>
        <FeedbackControl></FeedbackControl>
      </header>
      <div className="text-base leading-tight text-gray-800 whitespace-pre-wrap mb-8">
        {text}
      </div>
      <Sources showDisclaimer sources={sources} />
    </div>
  );
};
