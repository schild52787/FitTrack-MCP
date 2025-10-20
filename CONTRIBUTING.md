# Contributing to FitTrack MCP Server

Thank you for your interest in contributing to FitTrack MCP Server! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and environment details
   - Relevant logs or error messages

### Suggesting Enhancements

1. Check if the enhancement has been suggested
2. Create an issue describing:
   - Use case and motivation
   - Proposed solution
   - Alternative approaches considered
   - Impact on existing functionality

### Pull Requests

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run syntax check
   python -m py_compile fittrack_mcp.py

   # Test in stdio mode
   python fittrack_mcp.py

   # Test in HTTP mode
   uvicorn fittrack_mcp:app --reload
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Use conventional commits:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Test additions/changes
   - `chore:` - Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description
   - Reference related issues
   - Ensure CI checks pass

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/FitTrack-MCP.git
cd FitTrack-MCP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black ruff mypy pytest pytest-asyncio
```

## Code Style

- **Formatting**: Use `black` with default settings
  ```bash
  black fittrack_mcp.py
  ```

- **Linting**: Use `ruff`
  ```bash
  ruff check fittrack_mcp.py
  ```

- **Type Checking**: Use `mypy`
  ```bash
  mypy fittrack_mcp.py
  ```

## Adding New Features

### Adding a New Tool

1. Define Pydantic input model:
```python
class NewToolInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    param1: str = Field(..., description="Parameter description")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN)
```

2. Implement the tool:
```python
@mcp.tool(
    name="new_tool",
    annotations={
        "title": "New Tool Title",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def new_tool(params: NewToolInput) -> str:
    """Tool description.

    Args:
        params: Input parameters

    Returns:
        Formatted response
    """
    try:
        # Implementation
        return "result"
    except Exception as e:
        logger.error(f"Error in new_tool: {e}")
        return f"Error: {str(e)}"
```

3. Update documentation:
   - Add tool to README.md
   - Update mcp_config.json
   - Add usage examples

### Adding a New Rehab Protocol

1. Add to `REHAB_PROTOCOLS` dictionary
2. Follow existing structure with phases
3. Include evidence-based exercises
4. Add key principles section
5. Update `RehabCondition` enum

## Testing

Currently, the project uses manual testing. Automated tests are welcome contributions!

### Manual Testing Checklist

- [ ] All tools work in stdio mode
- [ ] All tools work in HTTP/SSE mode
- [ ] Input validation works correctly
- [ ] Error handling works as expected
- [ ] Output formats (Markdown/JSON) both work
- [ ] AC joint safety validation works
- [ ] Late meal warnings trigger correctly
- [ ] Hydration calculations are accurate

## Documentation

- Update README.md for new features
- Update DEPLOYMENT.md for deployment changes
- Add inline comments for complex logic
- Update docstrings for all functions

## Questions?

Feel free to open an issue with your question or reach out via the project's communication channels.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
