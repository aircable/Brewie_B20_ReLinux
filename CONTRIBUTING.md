# Contributing

## Principles

- Prefer upstream Linux solutions over vendor-specific code.
- Automate repetitive engineering tasks.
- Keep board-specific code separate from generic tooling.
- Preserve original firmware artifacts without modification.
- Document assumptions and unknowns.
- Every new script should work with more than one board whenever possible.

## Coding Standards

- Python 3.11+
- Type hints
- pathlib instead of os.path
- argparse for CLI tools
- logging instead of print (except for CLI output)
- Black formatting
- Ruff linting

## Testing

Each new feature should include:

- A sample input (e.g., `script.fex`)
- Expected output
- Instructions for reproducing the result

## Documentation

Every significant engineering decision should be reflected in `ARCHITECTURE.md` or `DISCOVERY.md`. Code and documentation should evolve together.
