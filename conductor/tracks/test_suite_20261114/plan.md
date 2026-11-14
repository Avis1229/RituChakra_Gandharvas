# Implementation Plan: Unit & Integration Test Suite

## Phase 1: Test Infrastructure & Fixture Setup
- [ ] Task: Install test dependencies and configure test environment
  - [ ] Add `pytest` and `pytest-cov` to `.venv` and update `requirements.txt`
  - [ ] Create `pytest.ini` with standard flags, pythonpath, and test discovery filters
  - [ ] Create `tests/conftest.py` with mock NASA API payloads and sample ESP32 telemetry fixtures
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Core Data Ingestion & Calibration Tests
- [ ] Task: Write tests for NASA POWER module (`tests/test_nasa_power.py`)
  - [ ] Test successful API response parsing and `-999` value imputation
  - [ ] Test network exception handling and seamless fallback to `generate_synthetic_fallback`
  - [ ] Test schema validation and date formatting of generated climate DataFrame
- [ ] Task: Write tests for Community Node calibration (`tests/test_community_node.py`)
  - [ ] Test realistic ESP32 telemetry bounds (temperature, rain tips, 0–100% soil VWC)
  - [ ] Test sensor fusion formula ($X_{calibrated} = 0.75 \cdot X_{ground} + 0.25 \cdot X_{satellite}$)
  - [ ] Test calculation of calibration metrics and MAE error reduction (>65%)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Analytics, ML Model & Rotation Engine Tests
- [ ] Task: Write tests for Climate Shift Analysis (`tests/test_climate_analysis.py`)
  - [ ] Test decadal warming slope regression and annual precipitation anomalies
  - [ ] Test monsoon peak month shift detection and drought vulnerability index scoring
  - [ ] Test edge cases (empty data, single-year data, missing parameters)
- [ ] Task: Write tests for ML Crop Suitability Model (`tests/test_ml_model.py`)
  - [ ] Test synthetic baseline training, model convergence, and sub-millisecond inference
  - [ ] Test crop-specific scoring and agronomic penalty behavior (e.g., Rice vs. Bajra in drought)
  - [ ] Test feature importances extraction
- [ ] Task: Write tests for 3-Strategy Rotation Engine (`tests/test_rotation_engine.py`)
  - [ ] Verify Strategy 1 (Optimized Baseline with shifted planting calendar)
  - [ ] Verify Strategy 2 (Soil Builder with positive biological N fixation and water savings)
  - [ ] Verify Strategy 3 (Climate Resilient drought/thermal tolerance up to 42°C)
  - [ ] Verify multi-criteria comparison matrix and exportable advisory text generation
- [ ] Task: Write tests for Visualizer module (`tests/test_visualizer.py`)
  - [ ] Verify `create_climate_trend_chart` returns a valid Plotly Figure
  - [ ] Verify `create_seasonality_shift_chart`, `create_calibration_comparison_chart`, and `create_strategy_radar_comparison`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Full Coverage Verification & Quality Gate
- [ ] Task: Execute test suite and verify >80% code coverage
  - [ ] Run `pytest --cov=modules --cov-report=term-missing`
  - [ ] Address any coverage gaps in `modules/` to guarantee >80% threshold
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
