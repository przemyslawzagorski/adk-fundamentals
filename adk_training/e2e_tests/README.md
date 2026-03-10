# E2E Test Suite for ADK Training Modules

End-to-end tests for `adk_training/` modules to verify examples work correctly.

## Quick Start

```bash
# Run all automated tests
python adk_training/e2e_tests/run_all_tests.py

# Run individual test
python adk_training/e2e_tests/test_module_01.py
```

## Prerequisites

### Required
- Python 3.12+
- `google-adk` package installed
- Google Cloud credentials configured:
  ```bash
  gcloud auth application-default login
  ```

### Optional (for specific modules)
- **Module 03 (RAG)**: Vertex AI Search configured
  - Set `SEARCH_ENGINE_ID` or `SEARCH_DATASTORE_ID` in `.env`
  - Test will skip gracefully if not configured

- **Module 09 (SQLite)**: Database initialized
  ```bash
  python adk_training/module_09_database_simple/init_database.py
  ```

- **Module 09 (Postgres)**: MCP Toolbox running
  ```bash
  ./toolbox --tools-file adk_training/module_09_database_postgres/toolbox.yaml
  ```

## Test Coverage

### ✅ Automated Tests (9 modules)

| Module | Description | Key Tests |
|--------|-------------|-----------|
| 01 - Hello World | Basic LLM agent | Response generation, conversation context |
| 02 - Custom Tool | Tool invocation | Tool calls, state changes, inventory management |
| 03 - RAG Agent | Vertex AI Search | Search queries (skips if not configured) |
| 04 - Sequential Agent | Multi-agent pipeline | Sequential execution, output_keys |
| 05 - Human-in-Loop | Callbacks & approval | Treasury management, approval workflow |
| 07 - Parallel Agent | Concurrent execution | Parallel scouts, report aggregation |
| 08 - Loop Critique | Iterative refinement | Loop execution, max iterations |
| 11 - Memory Bank | Mock memory tools | Recall voyages, treasures, crew notes |
| 12 - Router Agent | Agent routing | Specialist selection, domain routing |

### 📝 Manual Tests (2 modules)

| Module | Description | Setup Required |
|--------|-------------|----------------|
| 09 - SQLite | Database agent | Run `init_database.py` |
| 09 - Postgres | MCP database | Start Toolbox server |

### ⏭️ Skipped Modules (6 modules)

| Module | Reason |
|--------|--------|
| 06 - Cloud Run | Deployment module |
| 10 - Debugging | No testable behavior |
| 13 - Agent Engine | Deployment module |
| 14 - BigQuery | Requires BigQuery setup |
| 15 - Gmail | Requires OAuth via `adk web` |
| 16 - Resilience | App wrapper incompatible |

## Test Architecture

### Programmatic Execution
Tests use async Python scripts with `InMemorySessionService`:

```python
session_service = InMemorySessionService()
session = await session_service.create_session(
    app_name="test_app",
    user_id="test_user"
)

response_text = await extract_response_text(
    root_agent,
    "User query here",
    session
)
```

### Shared Utilities (`utils.py`)
- `extract_response_text()`: Execute agent and get response
- `extract_response_with_tool_calls()`: Track tool invocations
- `validate_response_not_empty()`: Check response validity
- `print_test_header()`, `print_test_summary()`: Formatted output

### Timeout
- 30 seconds per test query
- Prevents hanging on slow responses

## Running Tests

### All Automated Tests
```bash
python adk_training/e2e_tests/run_all_tests.py
```

Output shows:
- ✅ Passed tests
- ❌ Failed tests
- 📝 Manual test instructions
- ⏭️ Skipped modules

### Individual Tests
```bash
# Module 01
python adk_training/e2e_tests/test_module_01.py

# Module 02
python adk_training/e2e_tests/test_module_02.py

# etc.
```

### Manual Tests
```bash
# SQLite (after running init_database.py)
python adk_training/e2e_tests/manual_tests/test_module_09_simple.py

# Postgres (after starting Toolbox)
python adk_training/e2e_tests/manual_tests/test_module_09_postgres.py
```

## Troubleshooting

### Test Hangs
- **Cause**: Agent waiting for response
- **Solution**: Check timeout settings in `utils.py`

### Import Errors
- **Cause**: Module paths not in `sys.path`
- **Solution**: Tests automatically add paths; check `sys.path.insert()` calls

### Authentication Errors
- **Cause**: GCP credentials not configured
- **Solution**: Run `gcloud auth application-default login`

### Module 03 Skipped
- **Cause**: Vertex AI Search not configured
- **Solution**: Set `SEARCH_ENGINE_ID` or `SEARCH_DATASTORE_ID` in `.env`
- **Note**: Test returns success (True) when skipped, not failure

### Module 09 Database Not Found
- **Cause**: SQLite database not initialized
- **Solution**: Run `python adk_training/module_09_database_simple/init_database.py`

### Module 09 MCP Connection Failed
- **Cause**: Toolbox server not running
- **Solution**: Start Toolbox: `./toolbox --tools-file toolbox.yaml`

### Rate Limit Errors
- **Cause**: Too many API calls to Gemini
- **Solution**: Wait a few minutes, or switch to `gemini-1.5-flash` model

## Test Output Format

Console only (no HTML reports):

```
================================================================================
ADK TRAINING - E2E TEST SUITE
================================================================================

--------------------------------------------------------------------------------
  AUTOMATED TESTS
--------------------------------------------------------------------------------

🚀 Running: Module 01: Hello World
   File: test_module_01.py

📋 Test: Basic greeting
✅ PASS: Basic greeting
   Response length: 156 chars

...

--------------------------------------------------------------------------------
  TEST SUMMARY
--------------------------------------------------------------------------------

Total Tests: 9
✅ Passed: 9
❌ Failed: 0
```

## Development

### Adding New Tests
1. Create `test_module_XX.py` in `e2e_tests/`
2. Import utilities from `utils.py`
3. Implement async test functions
4. Add to `AUTOMATED_TESTS` in `run_all_tests.py`

### Test Pattern
```python
async def test_example():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        user_id="test_user"
    )
    
    response_text = await extract_response_text(
        root_agent,
        "Query here",
        session
    )
    
    is_valid, error_msg = validate_response_not_empty(response_text)
    if not is_valid:
        print(f"❌ FAIL: {error_msg}")
        return False
    
    print(f"✅ PASS: Test description")
    return True
```

## License

Same as parent project.

