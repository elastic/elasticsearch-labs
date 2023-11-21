# Testing

The `nbtest` directory contains a tool that can validate Python notebooks. A
wrapper script to install and run this tool is in the `bin/nbtest` directory in
this repository.

Example usage:

```bash
bin/nbtest notebook/search/00-quick-start.ipynb
```

To test all notebooks, you can run `make` from the top-level directory:

```bash
make
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
