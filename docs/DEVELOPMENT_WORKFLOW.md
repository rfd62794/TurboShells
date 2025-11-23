# Development Workflow Guide

This document outlines the recommended development workflow for TurboShells contributors.

## 🌳 Branching Strategy

### Main Branches
- **main**: Production-ready code, always stable
- **develop**: Integration branch for features

### Feature Branches
- **feature/phase-name**: New features (e.g., `feature/pond-environment`)
- **bugfix/issue-description**: Bug fixes (e.g., `bugfix/save-corruption`)
- **refactor/component-name**: Code refactoring (e.g., `refactor/genetics-system`)

### Commit Message Format

Use the following format for commit messages:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

#### Types
- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **chore**: Maintenance tasks

#### Examples
```
feat(training): Add terrain-specific stat improvements

- Implement swim training from water terrain
- Add climb training from rock terrain
- Add speed training from grass terrain

Fixes #42

fix(save): Resolve save file corruption issue

Add validation and error handling for save operations
```

## 🔄 Daily Workflow

### 1. Start Work
```bash
# Switch to develop branch
git checkout develop

# Pull latest changes
git pull origin develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. During Development
```bash
# Stage changes
git add .

# Commit with proper message
git commit -m "feat(feature): Add new functionality"

# Push to remote
git push origin feature/your-feature-name
```

### 3. Quality Checks
Before committing or pushing, ensure:
- Code is formatted with Black: `black .`
- Code passes Pylint: `pylint .`
- Tests pass: `pytest tests/`
- Pre-commit hooks run automatically

### 4. Complete Work
```bash
# Switch to develop
git checkout develop

# Pull latest changes
git pull origin develop

# Merge feature branch
git merge feature/your-feature-name

# Push to develop
git push origin develop

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## 📋 Code Review Process

### Before Submitting
1. **Self-Review**: Review your own code first
2. **Test Coverage**: Ensure new code has tests
3. **Documentation**: Update relevant documentation
4. **Style**: Follow project coding standards

### Pull Request Requirements
- Clear title and description
- Link to relevant issues
- Tests pass
- Code is reviewed and approved
- No merge conflicts

## 🧪 Testing Strategy

### Test Categories
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Manual Testing**: Playtesting for game features

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_main_game.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 🚀 Release Process

### Pre-Release Checklist
- [ ] All tests pass
- [ ] Code is documented
- [ ] Version is updated
- [ ] Changelog is updated
- [ ] Performance is acceptable

### Release Steps
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. Merge to main branch
5. Deploy if necessary

## 🛠️ Development Tools

### Pre-commit Hooks
Pre-commit hooks automatically run before each commit:
- Black formatting
- Pylint linting
- Basic validation

### Manual Tools
```bash
# Format code
black .

# Lint code
pylint .

# Run tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=. --cov-report=html
```

## 📝 Documentation

### Code Documentation
- Add docstrings to all public functions
- Use type hints where appropriate
- Comment complex logic

### Project Documentation
- Update README.md for user-facing changes
- Update TODO.md for development progress
- Update ARCHITECTURE.md for structural changes

## 🐛 Bug Reporting

### Bug Report Template
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Go to...
2. Click on...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10]
- Python version: [e.g., 3.9]
- Game version: [e.g., 2.4.0]

## Additional Context
Screenshots, logs, or other relevant information
```

## 🎯 Best Practices

### Code Quality
- Write clean, readable code
- Follow PEP 8 guidelines
- Use meaningful variable names
- Keep functions small and focused

### Performance
- Profile before optimizing
- Consider memory usage
- Test on different hardware

### Security
- Validate user input
- Handle errors gracefully
- Don't expose sensitive information

### Collaboration
- Communicate changes early
- Review code thoroughly
- Be constructive in feedback
- Help others learn
