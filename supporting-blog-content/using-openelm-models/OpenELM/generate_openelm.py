#
# For licensing see accompanying LICENSE file.
# Copyright (C) 2024 Apple Inc. All Rights Reserved.
#

"""Module to generate OpenELM output given a model and an input prompt."""
import os
import logging
import time
import argparse
from typing import Optional, Union
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM


def generate(
    prompt: str,
    model: Union[str, AutoModelForCausalLM],
    hf_access_token: str = None,
    tokenizer: Union[str, AutoTokenizer] = "meta-llama/Llama-2-7b-hf",
    device: Optional[str] = None,
    max_length: int = 1024,
    assistant_model: Optional[Union[str, AutoModelForCausalLM]] = None,
    generate_kwargs: Optional[dict] = None,
) -> str:
    """Generates output given a prompt.

    Args:
        prompt: The string prompt.
        model: The LLM Model. If a string is passed, it should be the path to
            the hf converted checkpoint.
        hf_access_token: Hugging face access token.
        tokenizer: Tokenizer instance. If model is set as a string path,
            the tokenizer will be loaded from the checkpoint.
        device: String representation of device to run the model on. If None
            and cuda available it would be set to cuda:0 else cpu.
        max_length: Maximum length of tokens, input prompt + generated tokens.
        assistant_model: If set, this model will be used for
            speculative generation. If a string is passed, it should be the
            path to the hf converted checkpoint.
        generate_kwargs: Extra kwargs passed to the hf generate function.

    Returns:
        output_text: output generated as a string.
        generation_time: generation time in seconds.

    Raises:
        ValueError: If device is set to CUDA but no CUDA device is detected.
        ValueError: If tokenizer is not set.
        ValueError: If hf_access_token is not specified.
    """
    if not device:
        if torch.cuda.is_available() and torch.cuda.device_count():
            device = "cuda:0"
            logging.warning(
                "inference device is not set, using cuda:0, %s",
                torch.cuda.get_device_name(0),
            )
        else:
            device = "cpu"
            logging.warning(
                ("No CUDA device detected, using cpu, " "expect slower speeds.")
            )

    if "cuda" in device and not torch.cuda.is_available():
        raise ValueError("CUDA device requested but no CUDA device detected.")

    if not tokenizer:
        raise ValueError("Tokenizer is not set in the generate function.")

    if not hf_access_token:
        raise ValueError(
            (
                "Hugging face access token needs to be specified. "
                "Please refer to https://huggingface.co/docs/hub/security-tokens"
                " to obtain one."
            )
        )

    if isinstance(model, str):
        checkpoint_path = model
        model = AutoModelForCausalLM.from_pretrained(
            checkpoint_path, trust_remote_code=True
        )
    model.to(device).eval()
    if isinstance(tokenizer, str):
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer,
            token=hf_access_token,
        )

    # Speculative mode
    draft_model = None
    if assistant_model:
        draft_model = assistant_model
        if isinstance(assistant_model, str):
            draft_model = AutoModelForCausalLM.from_pretrained(
                assistant_model, trust_remote_code=True
            )
        draft_model.to(device).eval()

    # Prepare the prompt
    tokenized_prompt = tokenizer(prompt)
    tokenized_prompt = torch.tensor(tokenized_prompt["input_ids"], device=device)

    tokenized_prompt = tokenized_prompt.unsqueeze(0)

    # Generate
    stime = time.time()
    output_ids = model.generate(
        tokenized_prompt,
        max_length=max_length,
        pad_token_id=0,
        assistant_model=draft_model,
        **(generate_kwargs if generate_kwargs else {}),
    )
    generation_time = time.time() - stime

    output_text = tokenizer.decode(output_ids[0].tolist(), skip_special_tokens=True)

    return output_text, generation_time


def openelm_generate_parser():
    """Argument Parser"""

    class KwargsParser(argparse.Action):
        """Parser action class to parse kwargs of form key=value"""

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, dict())
            for val in values:
                if "=" not in val:
                    raise ValueError(
                        (
                            "Argument parsing error, kwargs are expected in"
                            " the form of key=value."
                        )
                    )
                kwarg_k, kwarg_v = val.split("=")
                try:
                    converted_v = int(kwarg_v)
                except ValueError:
                    try:
                        converted_v = float(kwarg_v)
                    except ValueError:
                        converted_v = kwarg_v
                getattr(namespace, self.dest)[kwarg_k] = converted_v

    parser = argparse.ArgumentParser("OpenELM Generate Module")
    parser.add_argument(
        "--model",
        dest="model",
        help="Path to the hf converted model.",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--hf_access_token",
        dest="hf_access_token",
        help='Hugging face access token, starting with "hf_".',
        type=str,
    )
    parser.add_argument(
        "--prompt",
        dest="prompt",
        help="Prompt for LLM call.",
        default="",
        type=str,
    )
    parser.add_argument(
        "--device",
        dest="device",
        help="Device used for inference.",
        type=str,
    )
    parser.add_argument(
        "--max_length",
        dest="max_length",
        help="Maximum length of tokens.",
        default=256,
        type=int,
    )
    parser.add_argument(
        "--assistant_model",
        dest="assistant_model",
        help=(
            (
                "If set, this is used as a draft model "
                "for assisted speculative generation."
            )
        ),
        type=str,
    )
    parser.add_argument(
        "--generate_kwargs",
        dest="generate_kwargs",
        help="Additional kwargs passed to the HF generate function.",
        type=str,
        nargs="*",
        action=KwargsParser,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = openelm_generate_parser()
    prompt = args.prompt

    output_text, genertaion_time = generate(
        prompt=prompt,
        model=args.model,
        device=args.device,
        max_length=args.max_length,
        assistant_model=args.assistant_model,
        generate_kwargs=args.generate_kwargs,
        hf_access_token=args.hf_access_token,
    )

    print_txt = (
        f'\r\n{"=" * os.get_terminal_size().columns}\r\n'
        "\033[1m Prompt + Generated Output\033[0m\r\n"
        f'{"-" * os.get_terminal_size().columns}\r\n'
        f"{output_text}\r\n"
        f'{"-" * os.get_terminal_size().columns}\r\n'
        "\r\nGeneration took"
        f"\033[1m\033[92m {round(genertaion_time, 2)} \033[0m"
        "seconds.\r\n"
    )
    print(print_txt)
