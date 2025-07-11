# GEMINI.md

## Project Overview
This is a Django-based web application for Simple Work Schedule Management (swsm).

## Key Technologies
- Python: 3.9.2 (as per README.md, though current environment is 3.12.5)
- Django: 3.2.9
- Database: SQLite3 (default)

## Testing Status
- **Model Tests**: Completed for all models in `euser` and `swsm` applications.
- **Linting**: `flake8` is used for code style checks. All test files currently pass `flake8` checks.

## Conventions and Notes
- Custom user model (`euser.User`) is in use.
- `flake8` checks should be performed on all Python code changes.
- When committing changes, use a temporary file for the commit message (e.g., `git commit -F .git/COMMIT_EDITMSG`) to avoid shell interpretation issues with special characters or multi-line messages.
