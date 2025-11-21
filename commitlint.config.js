module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Type must be one of these
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation only
        'style',    // Code style (formatting, missing semi colons, etc)
        'refactor', // Code change that neither fixes a bug nor adds a feature
        'perf',     // Performance improvement
        'test',     // Adding or updating tests
        'build',    // Changes to build system or dependencies
        'ci',       // CI/CD changes
        'chore',    // Other changes that don't modify src or test files
        'revert',   // Revert a previous commit
      ],
    ],
    // Subject line cannot be empty
    'subject-empty': [2, 'never'],
    // Subject line max length (50 chars enforced)
    'subject-max-length': [2, 'always', 50],
    // Subject must be lowercase
    'subject-case': [2, 'always', 'lower-case'],
    // Body max line length (72 chars)
    'body-max-line-length': [2, 'always', 72],
    // Type must be lowercase
    'type-case': [2, 'always', 'lower-case'],
    // Type cannot be empty
    'type-empty': [2, 'never'],
    // Scope is required
    'scope-empty': [2, 'never'],
    // Scope must be lowercase
    'scope-case': [2, 'always', 'lower-case'],
  },
};
