# Copilot Instructions for Test Automation Framework

## Project Overview

This is a **Desktop UI Test Automation Framework** for Windows applications. It automates GUI interactions via `pywinauto` (UIA/Win32 backends), captures screenshots, and generates structured JSON reports.

### Architecture Pattern: Modular Action-Based Design

- **Core Driver**: [src/core/test_executor.py](src/core/test_executor.py) — orchestrates test execution (app lifecycle → test suites → test cases → actions)
- **Actions Layer**: [src/actions/](src/actions/) — pluggable actions (click, type, read, wait, etc.) via `ActionFactory`
- **App Manager**: [src/core/app_manager.py](src/core/app_manager.py) — Windows process lifecycle, `pywinauto` connection
- **Data Models**: [src/models/test_script.py](src/models/test_script.py) & [src/models/test_result.py](src/models/test_result.py) — dataclass-based JSON serialization
- **Logger**: [src/utils/logger.py](src/utils/logger.py) — dual output (colored console + timestamped file logs)

## Critical Workflows

### Running Tests

```bash
# Default: config/test_cristal_script.json
python main.py

# Custom script
python main.py config/test_app_script.json

# Skip JSON report generation
python main.py --no-report
```

### Adding New Action Types

1. **Create action class** in [src/actions/](src/actions/) inheriting `BaseAction`
2. **Implement `_execute_action(action: Action)`** — the core logic
3. **Register in `ActionFactory._action_map`** in [src/actions/__init__.py](src/actions/__init__.py)

Example: [src/actions/click_action.py](src/actions/click_action.py) uses `app_manager.find_control()` + `click()`.

For **clicking on text/labels**, use [src/actions/click_label_action.py](src/actions/click_label_action.py):
```json
{
  "type": "click_label",
  "description": "Click on a label or text",
  "value": "Text to find and click",
  "screenshot_on_success": true
}
```

### Test Script Format

JSON structure defined by schema in [src/models/test_script.py](src/models/test_script.py):
- **Application**: name, path, arguments, backend (`uia`|`win32`), timeouts
- **TestSuite**: list of test cases with IDs and tags
- **TestCase**: list of **Action** objects (type, control selector, screenshot flags, continue_on_failure)

Example: [config/test_app_script.json](config/test_app_script.json)

## Key Patterns & Conventions

### 1. Action Execution Flow
```python
# BaseAction.execute() → _execute_action() → ActionResult
# Error handling: if continue_on_failure=True, suite continues; else stops
```

### 2. Control Selection
- **UIA backend**: `class_type` (e.g., "Edit") + `control` (automation ID)
- **Win32 backend**: `window_title` + `control` (class name)
- `app_manager.find_control(action)` wraps both backends

### 2b. Window Focus Management
- Use `app_manager.bring_to_foreground(window)` method from [src/core/app_manager.py](src/core/app_manager.py#L200)
- Combines `set_focus()` + win32 APIs (`ShowWindow`, `SetForegroundWindow`, `BringWindowToTop`)
- Critical for reliability with multi-window scenarios or background apps

### 3. Screenshot Strategy
- On success: `screenshot_on_success=True` → captured to [screenshots/](screenshots/) with `success_` prefix
- On failure: `screenshot_on_failure=True` (default) → `failure_` prefix
- Manual: use `screenshot` action type via [src/actions/dialog_action.py](src/actions/dialog_action.py)

### 4. Error Handling
- **Skip Recoverable Errors**: Set `continue_on_failure=True` for non-blocking actions
- **Fail-Fast**: Default behavior stops suite on error
- **Always Cleanup**: `TestExecutor` ensures app closure via `finally` block in [src/core/test_executor.py](src/core/test_executor.py#L80-L90)

### 5. Logging Inheritance
- All classes accept `logger: TestLogger` in `__init__()`
- Use `logger.info()`, `logger.error()`, `logger.debug()` (see [src/utils/logger.py](src/utils/logger.py))
- Logs written to `logs/test_run_<timestamp>.log` + colored console

### 6. Results & Reports
- Each action produces `ActionResult` (status, duration, error_msg, screenshot_path)
- Final `TestExecutionResult` serialized to `reports/` as JSON
- Schema: [src/models/test_result.py](src/models/test_result.py)

## Integration Points

### External Dependencies
- **pywinauto**: Desktop automation; requires Win32 APIs
- **pillow**: Screenshot capture
- **colorlog**: Colored console logging
- **jsonschema**: Test script validation

### Cross-Component Communication
- `TestExecutor` ← owns → `AppManager`, `ScreenshotManager`, `ActionFactory`
- `BaseAction` subclasses receive injected managers + logger (dependency injection pattern)
- All actions share single `AppManager` instance to maintain app window state

## Common Tasks for AI Agents

### Debugging Test Failures
1. Check `logs/test_run_<timestamp>.log` for action-level errors
2. Review `screenshots/failure_*.png` for visual state at failure
3. Examine [src/core/app_manager.py](src/core/app_manager.py#L40-L70) — control finding logic

### Adding Application Support
- Update [src/models/test_script.py](src/models/test_script.py) `Application` dataclass if new fields needed
- Extend `AppManager.find_control()` if UIA/Win32 selector logic changes

### Test Suite Reusability
- Tag test cases in JSON (`"tags": ["smoke", "regression"]`) — parsed in [src/models/test_script.py](src/models/test_script.py)
- Filter at executor level if needed (currently all enabled cases run)

## Code Style & Structure Assumptions

- **Dataclasses**: Use `@dataclass` for models with `from_dict()` factory methods
- **Type hints**: All functions annotated (enables IDE completion)
- **Docstrings**: Portuguese docstrings; single responsibility per method
- **Path handling**: Use `pathlib.Path` (not os.path)
- **Exceptions**: Custom exceptions for domain errors; let system exceptions bubble up for visibility
