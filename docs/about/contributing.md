# Contributing

Help make arepy-ui better!

## Ways to Contribute

- 🐛 **Report bugs** - Open an issue on GitHub
- 💡 **Suggest features** - Share your ideas
- 📝 **Improve docs** - Fix typos, add examples
- 🔧 **Submit PRs** - Code contributions welcome

## Development Setup

1. **Clone the repo**

    ```bash
    git clone https://github.com/Scr44gr/arepy-ui
    cd arepy-ui
    ```

2. **Install dependencies**

    ```bash
    uv sync --all-extras
    ```

3. **Run tests**

    ```bash
    uv run pytest
    ```

4. **Run examples**

    ```bash
    uv run python examples/demo.py
    ```

## Code Style

- Use type hints
- Follow PEP 8
- Write docstrings for public APIs
- Add tests for new features

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Reporting Issues

When reporting bugs, include:

- arepy-ui version
- Python version
- Minimal reproduction code
- Expected vs actual behavior

## Feature Requests

Open an issue with:

- Clear description of the feature
- Use case / motivation
- Optional: Proposed implementation

## Documentation

Docs are in `docs/` using MkDocs. To preview:

```bash
uv run mkdocs serve
```

## Code of Conduct

Be respectful and inclusive. We're all here to make games better!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
