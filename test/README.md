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
