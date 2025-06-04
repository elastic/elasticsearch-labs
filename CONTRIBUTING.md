# Contributing

If you would like to contribute new example apps to the `elasticsearch-labs` repo, we would love to hear from you!

## Before you start

Prior to opening a pull request, please:
1. Create an issue to [discuss the scope of your proposal](https://github.com/elastic/elasticsearch-labs/issues). We are happy to provide guidance to make for a pleasant contribution experience.
2. Sign the [Contributor License Agreement](https://www.elastic.co/contributor-agreement/). We are not asking you to assign copyright to us, but to give us the right to distribute your code without restriction. We ask this of all contributors in order to assure our users of the origin and continuing existence of the code. You only need to sign the CLA once.
3. Install pre-commit...

### Pre-commit hook

This repository has a pre-commit hook that ensures that your contributed code follows our guidelines. It is strongly recommended that you install the pre-commit hook on your locally cloned repository, as that will allow you to check the correctness of your submission without having to wait for our continuous integration build. To install the pre-commit hook, clone this repository and then run the following command from its top-level directory:

```bash
make install
```

If you do not have access to the `make` utility, you can also install the pre-commit hook with Python:

```bash
python -m venv .venv
.venv/bin/pip install -qqq -r requirements-dev.txt
.venv/bin/pre-commit install
```

Now it can happen that you get an error when you try to commit, for example if your code or your notebook was not formatted with the [black formatter](https://github.com/psf/black). In this case, please run this command from the repo root:

```bash
make pre-commit
```

If you now include the changed files in your commit, it should succeed.

## General instruction

- If the notebook or code sample requires signing up a Elastic cloud instance, make sure to add appropriate `utm_source` and `utm_content` in the cloud registration url. For example, the Elastic cloud sign up url for the Python notebooks should have `utm_source=github&utm_content=elasticsearch-labs-notebook` and code examples should have `utm_source=github&utm_content=elasticsearch-labs-samples`.
  
## Contributing to Python notebooks 📒

### Why

* The main goal of this repo is to help people learn about solving various problems with the Elastic Stack using step-by-step interactive guides and specific applications.
* Remember your target audience: developers who want to try out some technology with Elastic. They may not be familiar with all the technologies.

### Where

* Select a folder under [notebooks](notebooks/README.md) that matches the category of your notebook. If none of them match, create a new folder.

### What

* Add your `.ipynb` file to the folder.
* The notebook should be self-contained. Avoid cross-linking code, data files, configuration etc. from other folders.
* We prefer the `kebab-case` file naming convention.
* Please write simple code and concise documentation, where appropriate.
* Start with a text cell that summarizes what the notebook will demonstrate. Feel free to use images - sometimes a picture is worth a thousand words.
* Add a header and description section before each code cell. Explain in simple terms what the code will be doing and what the expected outcome is.
* When the output of a cell is relevant, preserve it in the notebook.
* Update the `README.md` file in the folder of the notebook.

### How

* We recommend building the notebook in an interactive environment, such as [Google Colab](https://colab.google/). This way you can test all the steps and capture the output.
* **Never leave any secrets in the code** (API keys, passwords etc). Also avoid hardcoding URLs and IDs that may change from user to user. Instead use environment variables that need to be set by the user while they are running the notebook.
* Test your notebook end to end before submitting a pull request.
* Example of a well-formed notebook: [question-answering.ipynb](notebooks/generative-ai/question-answering.ipynb).

### Automated testing

Some notebooks in this repository are automatically tested with our [nbtest](https://github.com/elastic/nbtest) tool and we welcome any new notebooks to also be included.

The following command shows how to run a notebook with our tester:

```bash
bin/nbtest notebook/search/00-quick-start.ipynb
```

The `bin/nbtest` script is a wrapper that install `nbtest`. Alternatively, you can install it directly on your own virtual environment with this command:

```bash
pip install elastic-nbtest
```

To run all supported notebooks under this tool, run the following from the top-level directory of this repository:

```bash
make test
```

If you want to test under a previous release of Elasticsearch, you can define the `ES_STACK` variable with the target version so that notebooks that are not intended for that or previous versions are skipped. For example, here is how to only run tests for the 8.12 release of Elasticsearch:

```bash
ES_STACK=8.12 make test
```

Any notebooks that are added in subdirectories under `notebooks` are automatically picked up for testing. Notebooks that are known to not be suitable for automatic testing should be added to the list of exempt tests in the `bin/find_notebooks_to_test.sh` script. If the notebook should never be tested, add it to the `EXEMPT_NOTEBOOKS` list. If the notebook should be tested only under some versions of Elasticsearch, then add it to the appropriate versioned exemption list. For example, the `EXEMPT_NOTEBOOKS__8_12` list should include notebooks that are not be tested under releases 8.12 and older. New versioned lists are automatically recognized and can be added as needed.

## Contributing to example applications 💻

### Why

* The main goal of this repo is to help people learn about solving various problems with the Elastic Stack using step-by-step interactive guides and specific applications.
* Remember your target audience: developers who want to try out some technology with Elastic. They may not be familiar with all the technologies.

### Where

* Select a folder under [example-apps](example-apps/README.md) that matches the category of your applications. If none of them match, create a new folder.
* Create a folder under the category for your applications.

### What

* Add your app's files to the folder.
* The app should be self-contained. Avoid cross-linking code, data files, configuration etc. from other folders.
* Please write simple code and concise documentation, where appropriate.
* Add a `README.md` file in the root folder of the app:
  * Summarize what the app will demonstrate. Feel free to use images - sometimes a picture is worth a thousand words.
  * List language requirements in the readme file, e.g. "Python 3.6+".
  * List clear instructions for installing and running the example app in the readme file. This includes
  * Upload sample data files as necessary, or instructions for downloading them from an external source. Consider the license for any datasets.
  * Mention the version of the Elastic Stack that the example was tested with.

### How

* **Never leave any secrets in the code** (API keys, passwords etc). Also avoid hardcoding URLs and IDs that may change from user to user. Instead use environment variables that need to be set by the user while they are running the app.
* Test your app end to end before submitting a pull request.
* Example of a well-formed app: [OpenAI-JS](example-apps/openai-embeddings/README.md).

## Examples for the Elastic Search Labs Blog

If you are contributing an example corresponding to a blog post, use the folder `supporting-blog-content`. 

### Troubleshooting

- If the pre-commit checks are failing. You may want to try running the checks this way:

  ```
  python -m venv .venv
  .venv/bin/pip install -qqq -r requirements-dev.txt
  .venv/bin/pre-commit install
  ```

- If you are still having issues, you may want to double-check that your code is in the folder `supporting-blog-content`. 