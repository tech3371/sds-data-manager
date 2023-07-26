# Documentation

## Building documentation

1. Install the documentation dependencies
2. Build the html documents under the `docs` directory

Using poetry:

```bash
# Install the optional documentation dependencies
poetry install -E docs
# Make the html documentation
cd docs/source
poetry run sphinx-build . build
# View the documentation
open ../build/html/index.html
```

Using pip:

```bash
# Export requirements from poetry
poetry export --with=dev > requirements.txt
# Install the optional documentation dependencies
pip install -r requirements.txt
# Make the html documentation
make -C docs html
# View the documentation
open docs/_build/html/index.html
```
