# `nbtest`

The `nbtest` directory contains a tool that can validate Python notebooks. A
wrapper script to install and run this tool is in the `bin/nbtest` directory in
this repository.

Example usage:

```bash
bin/nbtest notebook/search/00-quick-start.ipynb
```

To test all notebooks that are supported under this tool, you can run `make`
from the top-level directory:

```bash
make
```

## How it works

`nbtest` runs all the code cells in the notebook in order from top to bottom,
and reports two error situations:

- If any code cells raise an unexpected exception
- If any code cells that have output saved in the notebook generate a different output (not counting specially designated sections, see the "Configuration" section below)

Something to keep in mind when designing notebooks that are testable is that
for any operations that are asynchronous it is necessary to add code that
blocks until these operations complete, so that the entire notebook can
execute in batch mode without errors.

## Configuration

`nbtest` looks for a configuration file named `.nbtest.yml` in the same
directory as the target notebook. If the configuration file is found, it is
imported and applied while the notebook runs.

There is currently one supported configuration variable, called `masks`. This
variable can be set to a list of regular expresssions for details in the output
of cells that are variable in nature and should be masked when comparing the
previously stored output against output from the current run.

Here is an example `.nbtest.yml` file:

```yaml
masks:
- "'name': '[^']+'"
- "'cluster_name': '[^']+'"
- "'cluster_uuid': '[^']+'"
- "'build_flavor': '[^']+'"
- '[0-9]+\.[0-9]+\.[0-9]+'
- "'build_hash': '[^']+'"
- "'build_date': '[^']+'"
```

## Handling of `getpass`

The `nbtest` script runs the notebooks with an alternative version of the
`getpass()` function that looks for requested values in environment variables
that need to be set before invoking the script.

Consider the following example, which is used in many Elastic notebooks:

```python
CLOUD_ID = getpass("Elastic Cloud ID:")
ELASTIC_API_KEY = getpass("Elastic Api Key:")
```

The `getpass()` function used by `nbtest` takes the prompt given as an
argument, and converts it to an environment variable name with the following
rules:

- Spaces are converted to underscores
- Non-alphanumeric characters are removed
- Letters are uppercased

In the above example, the variables that will be used are `ELASTIC_CLOUD_ID`
and `ELASTIC_API_KEY`.

## Set up and tear down procedures

Sometimes it is necessary to perform "set up" and/or "tear down" operations
before and after a notebook runs. `nbtest` will look for notebooks with special
names designated as set up or tear down and execute those notebooks to perform
any necessary code.

Note that if errors occur while executing a set up or tear down notebook, the
errors are reported, but are not counted as a test failure.

### Set up notebooks

`nbtest` will look for the following notebooks names and execute any that are
found before running the target notebook:

- `_nbtest_setup.ipynb`
- `_nbtest_setup.[notebook-name].ipynb`

The generic notebook can be used for general set up logic that applies to more
than one notebook in the same directory. Inside these notebooks, the
`NBTEST["notebook"]` expression can be used to obtain the name of the notebook
under test.

### Tear down notebooks

`nbtest` will look for the following notebooks names and execute any that are
found after running the target notebook, regardless of the testing having
succeeded or failed:

- `_nbtest_teardown.[notebook-name].ipynb`
- `_nbtest_teardown.ipynb`

These notebooks are inteded for cleanup that needs to happen after a text, for
example to delete indexes. As in the set up case, `NBTEST["notebook"]` is set
to the notebook that was tested.
