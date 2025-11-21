# Commit Message Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Components

- **type** (required): The type of change
- **scope** (optional): The area of the codebase affected
- **subject** (required): Short description in present tense
- **body** (optional): Detailed explanation
- **footer** (optional): Breaking changes, issue references

## Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(browser): add retry logic for element detection` |
| `fix` | Bug fix | `fix(config): handle missing environment variables` |
| `docs` | Documentation only | `docs: update installation instructions` |
| `style` | Code style/formatting | `style: format with black` |
| `refactor` | Code restructuring | `refactor(detector): simplify reward detection logic` |
| `perf` | Performance improvement | `perf(browser): reduce page load timeout` |
| `test` | Add/update tests | `test(orchestrator): add integration tests` |
| `build` | Build system/dependencies | `build: update playwright to 1.41.0` |
| `ci` | CI/CD changes | `ci: add commit message validation workflow` |
| `chore` | Other changes | `chore: update .gitignore` |
| `revert` | Revert previous commit | `revert: revert "feat: add new feature"` |

## Rules

### Subject Line
- ✅ Use lowercase
- ✅ Maximum 72 characters
- ✅ Use imperative mood ("add" not "added")
- ✅ No period at the end
- ❌ Don't capitalize first letter (except proper nouns)

### Body
- Maximum 100 characters per line
- Wrap text for readability
- Explain what and why, not how

### Examples

#### Good Examples

```bash
feat(browser): add playwright implementation

Implement PlaywrightBrowserManager as primary automation framework.
Includes context management, screenshot capability, and error handling.

Closes #123
```

```bash
fix(config): validate required environment variables

Add validation in ConfigurationManager to check for required vars.
Raises ConfigurationError with helpful message if vars are missing.
```

```bash
docs: add commit message convention guide

Create COMMIT_CONVENTION.md to document our commit standards
for new contributors.
```

```bash
test(detector): add unit tests for reward detection

Add comprehensive tests covering:
- Element detection strategies
- Reward claiming workflow
- Error handling scenarios
```

#### Bad Examples

```bash
# ❌ No type
Updated the browser manager

# ❌ Type in uppercase
FEAT: new feature

# ❌ Subject too long
feat: add a new feature that implements very complex logic with many different components and subsystems

# ❌ Period at end
feat: add new feature.

# ❌ Past tense
feat: added new feature

# ❌ Capitalized subject
feat: Add new feature
```

## Enforcement

### Local (Pre-commit Hooks)
Commits are validated locally before they reach the repository:
```bash
# Setup (one-time)
uv run pre-commit install --hook-type commit-msg

# Your commits are now automatically checked
git commit -m "feat: add new feature"
```

### CI/CD (GitHub Actions)
All commits are validated in CI:
- On push to main/develop branches
- On all commits in pull requests

Failed validation will block the CI pipeline.

## Bypassing (Emergency Only)

```bash
# Skip local hooks (NOT recommended)
git commit --no-verify -m "feat: emergency fix"
```

Note: CI validation cannot be bypassed.

## Tools

- **commitlint**: Validates commit messages
- **pre-commit**: Runs validation hooks locally
- **GitHub Actions**: Runs validation in CI

## Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [commitlint Documentation](https://commitlint.js.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
