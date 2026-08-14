# Contributing to SuperLayer

Thank you for contributing.

## Development workflow

1. Create a branch from `main`.
2. Keep changes focused and avoid committing QGIS profile caches or distribution ZIP files.
3. Run the test suite from the repository root:

   ```bash
   python -B -m unittest discover -q
   ```

4. Update `metadata.txt` and its changelog only when preparing a release.
5. Open a pull request describing the user-visible behavior, tests, and compatibility considerations.

## Code quality

- Keep Python syntax valid on supported QGIS Python versions.
- Avoid ambiguous variables such as `l`, `I`, and `O` (Flake8 E741).
- Do not use `shell=True`, dynamic `eval`/`exec`, hard-coded credentials, or unsafe deserialization.
- Preserve user data and require explicit confirmation for destructive file operations.

## Translations

Commit editable `.ts` translation sources to GitHub. Compiled `.qm` files are included in the QGIS distribution package.

## License

By contributing, you agree that your contribution is licensed under `GPL-3.0-or-later`.
