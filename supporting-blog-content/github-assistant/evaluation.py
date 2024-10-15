import logging
import sys
import os
import pandas as pd
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response
from llama_index.core.evaluation import (
    DatasetGenerator,
    RelevancyEvaluator,
    FaithfulnessEvaluator,
    EvaluationResult,
)
from llama_index.llms.openai import OpenAI
from tabulate import tabulate
import textwrap
import argparse
import traceback
from httpx import ReadTimeout

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

parser = argparse.ArgumentParser(
    description="Process documents and questions for evaluation."
)
parser.add_argument(
    "--num_documents",
    type=int,
    default=None,
    help="Number of documents to process (default: all)",
)
parser.add_argument(
    "--skip_documents",
    type=int,
    default=0,
    help="Number of documents to skip at the beginning (default: 0)",
)
parser.add_argument(
    "--num_questions",
    type=int,
    default=None,
    help="Number of questions to process (default: all)",
)
parser.add_argument(
    "--skip_questions",
    type=int,
    default=0,
    help="Number of questions to skip at the beginning (default: 0)",
)
parser.add_argument(
    "--process_last_questions",
    action="store_true",
    help="Process last N questions instead of first N",
)
args = parser.parse_args()

load_dotenv(".env")

reader = SimpleDirectoryReader("/tmp/elastic/production-readiness-review")
documents = reader.load_data()
print(f"First document: {documents[0].text}")
print(f"Second document: {documents[1].text}")
print(f"Thrid document: {documents[2].text}")


if args.skip_documents > 0:
    documents = documents[args.skip_documents :]

if args.num_documents is not None:
    documents = documents[: args.num_documents]

print(f"Number of documents loaded: {len(documents)}")

llm = OpenAI(model="gpt-4o", request_timeout=120)

data_generator = DatasetGenerator.from_documents(documents, llm=llm)

try:
    eval_questions = data_generator.generate_questions_from_nodes()
    if isinstance(eval_questions, str):
        eval_questions_list = eval_questions.strip().split("\n")
    else:
        eval_questions_list = eval_questions
    eval_questions_list = [q for q in eval_questions_list if q.strip()]

    if args.skip_questions > 0:
        eval_questions_list = eval_questions_list[args.skip_questions :]

    if args.num_questions is not None:
        if args.process_last_questions:
            eval_questions_list = eval_questions_list[-args.num_questions :]
        else:
            eval_questions_list = eval_questions_list[: args.num_questions]

    print("\All available questions generated:")
    for idx, q in enumerate(eval_questions):
        print(f"{idx}. {q}")

    print("\nGenerated questions:")
    for idx, q in enumerate(eval_questions_list, start=1):
        print(f"{idx}. {q}")
except ReadTimeout as e:
    print(
        "Request to Ollama timed out during question generation. Please check the server or increase the timeout duration."
    )
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"An error occurred while generating questions: {e}")
    traceback.print_exc()
    sys.exit(1)

print(f"\nTotal number of questions generated: {len(eval_questions_list)}")

evaluator_relevancy = RelevancyEvaluator(llm=llm)
evaluator_faith = FaithfulnessEvaluator(llm=llm)

vector_index = VectorStoreIndex.from_documents(documents)


def display_eval_df(
    query: str,
    response: Response,
    eval_result_relevancy: EvaluationResult,
    eval_result_faith: EvaluationResult,
) -> None:
    relevancy_feedback = getattr(eval_result_relevancy, "feedback", "")
    relevancy_passing = getattr(eval_result_relevancy, "passing", False)
    relevancy_passing_str = "Pass" if relevancy_passing else "Fail"

    relevancy_score = 1.0 if relevancy_passing else 0.0

    faithfulness_feedback = getattr(eval_result_faith, "feedback", "")
    faithfulness_passing_bool = getattr(eval_result_faith, "passing", False)
    faithfulness_passing = "Pass" if faithfulness_passing_bool else "Fail"

    def wrap_text(text, width=50):
        if text is None:
            return ""
        text = str(text)
        text = text.replace("\r", "")
        lines = text.split("\n")
        wrapped_lines = []
        for line in lines:
            wrapped_lines.extend(textwrap.wrap(line, width=width))
            wrapped_lines.append("")
        return "\n".join(wrapped_lines)

    if response.source_nodes:
        source_content = wrap_text(response.source_nodes[0].node.get_content())
    else:
        source_content = ""

    eval_data = {
        "Query": wrap_text(query),
        "Response": wrap_text(str(response)),
        "Source": source_content,
        "Relevancy Response": relevancy_passing_str,
        "Relevancy Feedback": wrap_text(relevancy_feedback),
        "Relevancy Score": wrap_text(str(relevancy_score)),
        "Faith Response": faithfulness_passing,
        "Faith Feedback": wrap_text(faithfulness_feedback),
    }

    eval_df = pd.DataFrame([eval_data])

    print("\nEvaluation Result:")
    print(
        tabulate(
            eval_df, headers="keys", tablefmt="grid", showindex=False, stralign="left"
        )
    )


query_engine = vector_index.as_query_engine(llm=llm)

total_questions = len(eval_questions_list)
for idx, question in enumerate(eval_questions_list, start=1):
    try:
        response_vector = query_engine.query(question)
        eval_result_relevancy = evaluator_relevancy.evaluate_response(
            query=question, response=response_vector
        )
        eval_result_faith = evaluator_faith.evaluate_response(response=response_vector)

        print(f"\nProcessing Question {idx} of {total_questions}:")
        display_eval_df(
            question, response_vector, eval_result_relevancy, eval_result_faith
        )
    except ReadTimeout as e:
        print(f"Request to OpenAI timed out while processing question {idx}.")
        traceback.print_exc()
        continue
    except Exception as e:
        print(f"An error occurred while processing question {idx}: {e}")
        traceback.print_exc()
        continue
