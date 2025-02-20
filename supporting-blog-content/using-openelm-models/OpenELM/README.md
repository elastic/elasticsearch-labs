---
license: other
license_name: apple-sample-code-license
license_link: LICENSE
---

# OpenELM: An Efficient Language Model Family with Open Training and Inference Framework

*Sachin Mehta, Mohammad Hossein Sekhavat, Qingqing Cao, Maxwell Horton, Yanzi Jin, Chenfan Sun, Iman Mirzadeh, Mahyar Najibi, Dmitry Belenko, Peter Zatloukal, Mohammad Rastegari*

We introduce **OpenELM**, a family of **Open** **E**fficient **L**anguage **M**odels. OpenELM uses a layer-wise scaling strategy to efficiently allocate parameters within each layer of the transformer model, leading to enhanced accuracy. We pretrained OpenELM models using the [CoreNet](https://github.com/apple/corenet) library. We release both pretrained and instruction tuned models with 270M, 450M, 1.1B and 3B parameters.

Our pre-training dataset contains RefinedWeb, deduplicated PILE, a subset of RedPajama, and a subset of Dolma v1.6, totaling approximately 1.8 trillion tokens. Please check license agreements and terms of these datasets before using them.

See the list below for the details of each model:

- [OpenELM-270M](https://huggingface.co/apple/OpenELM-270M)                   
- [OpenELM-450M](https://huggingface.co/apple/OpenELM-450M)                   
- [OpenELM-1_1B](https://huggingface.co/apple/OpenELM-1_1B)                   
- [OpenELM-3B](https://huggingface.co/apple/OpenELM-3B)                       
- [OpenELM-270M-Instruct](https://huggingface.co/apple/OpenELM-270M-Instruct) 
- [OpenELM-450M-Instruct](https://huggingface.co/apple/OpenELM-450M-Instruct) 
- [OpenELM-1_1B-Instruct](https://huggingface.co/apple/OpenELM-1_1B-Instruct) 
- [OpenELM-3B-Instruct](https://huggingface.co/apple/OpenELM-3B-Instruct)     


```python

from transformers import AutoModelForCausalLM

openelm_270m = AutoModelForCausalLM.from_pretrained("apple/OpenELM-270M", trust_remote_code=True)
openelm_450m = AutoModelForCausalLM.from_pretrained("apple/OpenELM-450M", trust_remote_code=True)
openelm_1b = AutoModelForCausalLM.from_pretrained("apple/OpenELM-1_1B", trust_remote_code=True)
openelm_3b = AutoModelForCausalLM.from_pretrained("apple/OpenELM-3B", trust_remote_code=True)

openelm_270m_instruct = AutoModelForCausalLM.from_pretrained("apple/OpenELM-270M-Instruct", trust_remote_code=True)
openelm_450m_instruct = AutoModelForCausalLM.from_pretrained("apple/OpenELM-450M-Instruct", trust_remote_code=True)
openelm_1b_instruct = AutoModelForCausalLM.from_pretrained("apple/OpenELM-1_1B-Instruct", trust_remote_code=True)
openelm_3b_instruct = AutoModelForCausalLM.from_pretrained("apple/OpenELM-3B-Instruct", trust_remote_code=True)

```

## Usage

We have provided an example function to generate output from OpenELM models loaded via [HuggingFace Hub](https://huggingface.co/docs/hub/) in `generate_openelm.py`.

You can try the model by running the following command:
```
python generate_openelm.py --model [MODEL_NAME] --hf_access_token [HF_ACCESS_TOKEN] --prompt 'Once upon a time there was' --generate_kwargs repetition_penalty=1.2
```
Please refer to [this link](https://huggingface.co/docs/hub/security-tokens) to obtain your hugging face access token.

Additional arguments to the hugging face generate function can be passed via `generate_kwargs`. As an example, to speedup the inference, you can try [lookup token speculative generation](https://huggingface.co/docs/transformers/generation_strategies) by passing the `prompt_lookup_num_tokens` argument as follows:
```
python generate_openelm.py --model [MODEL_NAME] --hf_access_token [HF_ACCESS_TOKEN] --prompt 'Once upon a time there was' --generate_kwargs repetition_penalty=1.2 prompt_lookup_num_tokens=10
```
Alternatively, try model-wise speculative generation with an [assistive model](https://huggingface.co/blog/assisted-generation) by passing a smaller model through the `assistant_model` argument, for example:
```
python generate_openelm.py --model [MODEL_NAME] --hf_access_token [HF_ACCESS_TOKEN] --prompt 'Once upon a time there was' --generate_kwargs repetition_penalty=1.2 --assistant_model [SMALLER_MODEL_NAME]
```


## Main Results

### Zero-Shot

| **Model Size**                                                              | **ARC-c** | **ARC-e** | **BoolQ** | **HellaSwag** | **PIQA**  | **SciQ**  | **WinoGrande** | **Average** |
|-----------------------------------------------------------------------------|-----------|-----------|-----------|---------------|-----------|-----------|----------------|-------------|
| [OpenELM-270M](https://huggingface.co/apple/OpenELM-270M)                   | 26.45     | 45.08     | **53.98** | 46.71         | 69.75     | **84.70** | **53.91**      | 54.37       |
| [OpenELM-270M-Instruct](https://huggingface.co/apple/OpenELM-270M-Instruct) | **30.55** | **46.68** | 48.56     | **52.07**     | **70.78** | 84.40     | 52.72          | **55.11**   |
| [OpenELM-450M](https://huggingface.co/apple/OpenELM-450M)                   | 27.56     | 48.06     | 55.78     | 53.97         | 72.31     | 87.20     | 58.01          | 57.56       |
| [OpenELM-450M-Instruct](https://huggingface.co/apple/OpenELM-450M-Instruct) | **30.38** | **50.00** | **60.37** | **59.34**     | **72.63** | **88.00** | **58.96**      | **59.95**   |
| [OpenELM-1_1B](https://huggingface.co/apple/OpenELM-1_1B)                   | 32.34     | **55.43** | 63.58     | 64.81         | **75.57** | **90.60** | 61.72          | 63.44       |
| [OpenELM-1_1B-Instruct](https://huggingface.co/apple/OpenELM-1_1B-Instruct) | **37.97** | 52.23     | **70.00** | **71.20**     | 75.03     | 89.30     | **62.75**      | **65.50**   |
| [OpenELM-3B](https://huggingface.co/apple/OpenELM-3B)                       | 35.58     | 59.89     | 67.40     | 72.44         | 78.24     | **92.70** | 65.51          | 67.39       |
| [OpenELM-3B-Instruct](https://huggingface.co/apple/OpenELM-3B-Instruct)     | **39.42** | **61.74** | **68.17** | **76.36**     | **79.00** | 92.50     | **66.85**      | **69.15**   |

### LLM360

| **Model Size**                                                              | **ARC-c** | **HellaSwag** | **MMLU**  | **TruthfulQA** | **WinoGrande** | **Average** |
|-----------------------------------------------------------------------------|-----------|---------------|-----------|----------------|----------------|-------------|
| [OpenELM-270M](https://huggingface.co/apple/OpenELM-270M)                   | 27.65     | 47.15         | 25.72     | **39.24**      | **53.83**      | 38.72       |
| [OpenELM-270M-Instruct](https://huggingface.co/apple/OpenELM-270M-Instruct) | **32.51** | **51.58**     | **26.70** | 38.72          | 53.20          | **40.54**   |
| [OpenELM-450M](https://huggingface.co/apple/OpenELM-450M)                   | 30.20     | 53.86         | **26.01** | 40.18          | 57.22          | 41.50       |
| [OpenELM-450M-Instruct](https://huggingface.co/apple/OpenELM-450M-Instruct) | **33.53** | **59.31**     | 25.41     | **40.48**      | **58.33**      | **43.41**   |
| [OpenELM-1_1B](https://huggingface.co/apple/OpenELM-1_1B)                   | 36.69     | 65.71         | **27.05** | 36.98          | 63.22          | 45.93       |
| [OpenELM-1_1B-Instruct](https://huggingface.co/apple/OpenELM-1_1B-Instruct) | **41.55** | **71.83**     | 25.65     | **45.95**      | **64.72**      | **49.94**   |
| [OpenELM-3B](https://huggingface.co/apple/OpenELM-3B)                       | 42.24     | 73.28         | **26.76** | 34.98          | 67.25          | 48.90       |
| [OpenELM-3B-Instruct](https://huggingface.co/apple/OpenELM-3B-Instruct)     | **47.70** | **76.87**     | 24.80     | **38.76**      | **67.96**      | **51.22**   |


### OpenLLM Leaderboard

| **Model Size**                                                              | **ARC-c** | **CrowS-Pairs** | **HellaSwag** | **MMLU**  | **PIQA**  | **RACE**  | **TruthfulQA** | **WinoGrande** | **Average** |
|-----------------------------------------------------------------------------|-----------|-----------------|---------------|-----------|-----------|-----------|----------------|----------------|-------------|
| [OpenELM-270M](https://huggingface.co/apple/OpenELM-270M)                   | 27.65     | **66.79**       | 47.15         | 25.72     | 69.75     | 30.91     | **39.24**      | **53.83**      | 45.13       |
| [OpenELM-270M-Instruct](https://huggingface.co/apple/OpenELM-270M-Instruct) | **32.51** | 66.01           | **51.58**     | **26.70** | **70.78** | 33.78     | 38.72          | 53.20          | **46.66**   |
| [OpenELM-450M](https://huggingface.co/apple/OpenELM-450M)                   | 30.20     | **68.63**       | 53.86         | **26.01** | 72.31     | 33.11     | 40.18          | 57.22          | 47.69       |
| [OpenELM-450M-Instruct](https://huggingface.co/apple/OpenELM-450M-Instruct) | **33.53** | 67.44           | **59.31**     | 25.41     | **72.63** | **36.84** | **40.48**      | **58.33**      | **49.25**   |
| [OpenELM-1_1B](https://huggingface.co/apple/OpenELM-1_1B)                   | 36.69     | **71.74**       | 65.71         | **27.05** | **75.57** | 36.46     | 36.98          | 63.22          | 51.68       |
| [OpenELM-1_1B-Instruct](https://huggingface.co/apple/OpenELM-1_1B-Instruct) | **41.55** | 71.02           | **71.83**     | 25.65     | 75.03     | **39.43** | **45.95**      | **64.72**      | **54.40**   |
| [OpenELM-3B](https://huggingface.co/apple/OpenELM-3B)                       | 42.24     | **73.29**       | 73.28         | **26.76** | 78.24     | **38.76** | 34.98          | 67.25          | 54.35       |
| [OpenELM-3B-Instruct](https://huggingface.co/apple/OpenELM-3B-Instruct)     | **47.70** | 72.33           | **76.87**     | 24.80     | **79.00** | 38.47     | **38.76**      | **67.96**      | **55.73**   |

See the technical report for more results and comparison.

## Evaluation

### Setup

Install the following dependencies:

```bash

# install public lm-eval-harness

harness_repo="public-lm-eval-harness"
git clone https://github.com/EleutherAI/lm-evaluation-harness ${harness_repo}
cd ${harness_repo}
# use main branch on 03-15-2024, SHA is dc90fec
git checkout dc90fec
pip install -e .
cd ..

# 66d6242 is the main branch on 2024-04-01 
pip install datasets@git+https://github.com/huggingface/datasets.git@66d6242
pip install tokenizers>=0.15.2 transformers>=4.38.2 sentencepiece>=0.2.0

```

### Evaluate OpenELM

```bash

# OpenELM-270M
hf_model=apple/OpenELM-270M

# this flag is needed because lm-eval-harness set add_bos_token to False by default, but OpenELM uses LLaMA tokenizer which requires add_bos_token to be True
tokenizer=meta-llama/Llama-2-7b-hf
add_bos_token=True
batch_size=1

mkdir lm_eval_output

shot=0
task=arc_challenge,arc_easy,boolq,hellaswag,piqa,race,winogrande,sciq,truthfulqa_mc2
lm_eval --model hf \
        --model_args pretrained=${hf_model},trust_remote_code=True,add_bos_token=${add_bos_token},tokenizer=${tokenizer} \
        --tasks ${task} \
        --device cuda:0 \
        --num_fewshot ${shot} \
        --output_path ./lm_eval_output/${hf_model//\//_}_${task//,/_}-${shot}shot \
        --batch_size ${batch_size} 2>&1 | tee ./lm_eval_output/eval-${hf_model//\//_}_${task//,/_}-${shot}shot.log

shot=5
task=mmlu,winogrande
lm_eval --model hf \
        --model_args pretrained=${hf_model},trust_remote_code=True,add_bos_token=${add_bos_token},tokenizer=${tokenizer} \
        --tasks ${task} \
        --device cuda:0 \
        --num_fewshot ${shot} \
        --output_path ./lm_eval_output/${hf_model//\//_}_${task//,/_}-${shot}shot \
        --batch_size ${batch_size} 2>&1 | tee ./lm_eval_output/eval-${hf_model//\//_}_${task//,/_}-${shot}shot.log

shot=25
task=arc_challenge,crows_pairs_english
lm_eval --model hf \
        --model_args pretrained=${hf_model},trust_remote_code=True,add_bos_token=${add_bos_token},tokenizer=${tokenizer} \
        --tasks ${task} \
        --device cuda:0 \
        --num_fewshot ${shot} \
        --output_path ./lm_eval_output/${hf_model//\//_}_${task//,/_}-${shot}shot \
        --batch_size ${batch_size} 2>&1 | tee ./lm_eval_output/eval-${hf_model//\//_}_${task//,/_}-${shot}shot.log

shot=10
task=hellaswag
lm_eval --model hf \
        --model_args pretrained=${hf_model},trust_remote_code=True,add_bos_token=${add_bos_token},tokenizer=${tokenizer} \
        --tasks ${task} \
        --device cuda:0 \
        --num_fewshot ${shot} \
        --output_path ./lm_eval_output/${hf_model//\//_}_${task//,/_}-${shot}shot \
        --batch_size ${batch_size} 2>&1 | tee ./lm_eval_output/eval-${hf_model//\//_}_${task//,/_}-${shot}shot.log

```


## Bias, Risks, and Limitations

The release of OpenELM models aims to empower and enrich the open research community by providing access to state-of-the-art language models. Trained on publicly available datasets, these models are made available without any safety guarantees. Consequently, there exists the possibility of these models producing outputs that are inaccurate, harmful, biased, or objectionable in response to user prompts. Thus, it is imperative for users and developers to undertake thorough safety testing and implement appropriate filtering mechanisms tailored to their specific requirements.

## Citation

If you find our work useful, please cite:

```BibTex 
@article{mehtaOpenELMEfficientLanguage2024,
	title = {{OpenELM}: {An} {Efficient} {Language} {Model} {Family} with {Open} {Training} and {Inference} {Framework}},
	shorttitle = {{OpenELM}},
	url = {https://arxiv.org/abs/2404.14619v1},
	language = {en},
	urldate = {2024-04-24},
	journal = {arXiv.org},
	author = {Mehta, Sachin and Sekhavat, Mohammad Hossein and Cao, Qingqing and Horton, Maxwell and Jin, Yanzi and Sun, Chenfan and Mirzadeh, Iman and Najibi, Mahyar and Belenko, Dmitry and Zatloukal, Peter and Rastegari, Mohammad},
	month = apr,
	year = {2024},
}

@inproceedings{mehta2022cvnets, 
     author = {Mehta, Sachin and Abdolhosseini, Farzad and Rastegari, Mohammad}, 
     title = {CVNets: High Performance Library for Computer Vision}, 
     year = {2022}, 
     booktitle = {Proceedings of the 30th ACM International Conference on Multimedia}, 
     series = {MM '22} 
}
```
