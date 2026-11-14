# Specification: Unit & Integration Test Suite

## 1. Overview
This track implements an automated, high-fidelity unit and integration test suite for the **Field Shift** decision-support platform using `pytest` and `pytest-cov`. It establishes robust quality gates for NASA climate data ingestion, community node sensor fusion, agricultural shift calculations, tabular Random Forest suitability prediction, and 3-strategy crop rotation generation.

## 2. Functional Requirements
1. **NASA POWER Module Tests (`tests/test_nasa_power.py`):**
   - Unit tests for `fetch_nasa_power_climate` verifying live format parsing and missing value imputation (`-999` replacements).
   - Mocked network failure scenarios verifying seamless fallback to `generate_synthetic_fallback`.
   - Validate structure, column schema, and data integrity of monthly climate records.
2. **Community Node Calibration Tests (`tests/test_community_node.py`):**
   - Validate generation of synthetic ESP32 ground-truth telemetry with realistic physical constraints (soil moisture bounds 0–100%, battery voltage, rain tips).
   - Verify calculation of calibration metrics (MAE reduction $>65\%$, accuracy gains for temperature and soil moisture).
   - Test sensor fusion formula $X_{calibrated} = \alpha \cdot X_{ground} + (1 - \alpha) \cdot X_{satellite}$ with $\alpha = 0.75$.
3. **Climate Shift Analysis Tests (`tests/test_climate_analysis.py`):**
   - Test temperature decadal slope regression and precipitation anomaly calculations.
   - Test monsoon peak shift detection (identifying shifts in maximum rainfall month).
   - Test edge cases (empty dataframes, single-year records, high-volatility rain regimes).
4. **ML Crop Suitability Model Tests (`tests/test_ml_model.py`):**
   - Test synthetic baseline initialization and model convergence within $<50\text{ MB}$ memory.
   - Verify deterministic scoring output ($0\text{–}100$) across all 12 crop catalog profiles.
   - Verify agronomic penalties (e.g., drought impact on Rice vs. Millets).
   - Test feature importance extraction.
5. **Rotation Engine Tests (`tests/test_rotation_engine.py`):**
   - Verify generation of all 3 distinct strategies:
     - Strategy 1: Optimized Baseline with shifted planting window.
     - Strategy 2: Soil Builder with positive biological nitrogen balance ($+45\text{ to }+85\text{ kg N/ha}$) and water savings.
     - Strategy 3: Climate Resilient crop with high thermal and drought tolerance.
   - Verify schema and data completeness of comparison table and text report.
6. **Visualizer Tests (`tests/test_visualizer.py`):**
   - Validate that Plotly figure generator functions return valid, renderable `go.Figure` instances with expected traces and layouts.

## 3. Non-Functional Requirements
- **Execution Speed:** Full test suite must execute in $< 5$ seconds on CPU.
- **Offline Determinism:** Zero external network dependency during standard test execution (all NASA API calls mocked).
- **Quality Gate:** Minimum **>80% code coverage** enforced across `modules/` using `pytest-cov`.

## 4. Acceptance Criteria
- [ ] `pytest` and `pytest-cov` installed and configured.
- [ ] Test files created under `tests/` covering all 6 core modules.
- [ ] All unit and integration tests pass with 0 failures and 0 warnings.
- [ ] Code coverage report demonstrates $>80\%$ total coverage across the codebase.
- [ ] Test command documented and runnable via `pytest --cov=modules --cov-report=term-missing`.

## 5. Out of Scope
- End-to-end browser automation for Streamlit UI (Selenium/Playwright) in this phase.
- Live hardware flashing tests on physical ESP32 boards (hardware simulation only).

