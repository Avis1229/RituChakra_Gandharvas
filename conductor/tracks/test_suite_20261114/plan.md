# Implementation Plan: Unit & Integration Test Suite

## Phase 1: Test Infrastructure & Fixture Setup [checkpoint: 1913e78]
- [x] Task: Install test dependencies and configure test environment (1913e78)
  - [x] Add `pytest` and `pytest-cov` to `.venv` and update `requirements.txt`
  - [x] Create `pytest.ini` with standard flags, pythonpath, and test discovery filters
  - [x] Create `tests/conftest.py` with mock NASA API payloads and sample ESP32 telemetry fixtures
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (1913e78)

## Phase 2: Core Data Ingestion & Calibration Tests [checkpoint: 04740f3]
- [x] Task: Write tests for NASA POWER module (`tests/test_nasa_power.py`) (3d2ea8d)
  - [x] Test successful API response parsing and `-999` value imputation
  - [x] Test network exception handling and seamless fallback to `generate_synthetic_fallback`
  - [x] Test schema validation and date formatting of generated climate DataFrame
- [x] Task: Write tests for Community Node calibration (`tests/test_community_node.py`) (1024264)
  - [x] Test realistic ESP32 telemetry bounds (temperature, rain tips, 0–100% soil VWC)
  - [x] Test sensor fusion formula ($X_{calibrated} = 0.75 \cdot X_{ground} + 0.25 \cdot X_{satellite}$)
  - [x] Test calculation of calibration metrics and MAE error reduction (>65%)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (04740f3)

## Phase 3: Analytics, ML Model & Rotation Engine Tests [checkpoint: 37e9568]
- [x] Task: Write tests for Climate Shift Analysis (`tests/test_climate_analysis.py`) (aa75cfc)
  - [x] Test decadal warming slope regression and annual precipitation anomalies
  - [x] Test monsoon peak month shift detection and drought vulnerability index scoring
  - [x] Test edge cases (empty data, single-year data, missing parameters)
- [x] Task: Write tests for ML Crop Suitability Model (`tests/test_ml_model.py`) (4000695)
  - [x] Test synthetic baseline training, model convergence, and sub-millisecond inference
  - [x] Test crop-specific scoring and agronomic penalty behavior (e.g., Rice vs. Bajra in drought)
  - [x] Test feature importances extraction
- [x] Task: Write tests for 3-Strategy Rotation Engine (`tests/test_rotation_engine.py`) (e781596)
  - [x] Verify Strategy 1 (Optimized Baseline with shifted planting calendar)
  - [x] Verify Strategy 2 (Soil Builder with positive biological N fixation and water savings)
  - [x] Verify Strategy 3 (Climate Resilient drought/thermal tolerance up to 42°C)
  - [x] Verify multi-criteria comparison matrix and exportable advisory text generation
- [x] Task: Write tests for Visualizer module (`tests/test_visualizer.py`) (37e9568)
  - [x] Verify `create_climate_trend_chart` returns a valid Plotly Figure
  - [x] Verify `create_seasonality_shift_chart`, `create_calibration_comparison_chart`, and `create_strategy_radar_comparison`
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (37e9568)

## Phase 4: Full Coverage Verification & Quality Gate [checkpoint: c98f5ff]
- [x] Task: Execute test suite and verify >80% code coverage (c98f5ff)
  - [x] Run `pytest --cov=modules --cov-report=term-missing`
  - [x] Address any coverage gaps in `modules/` to guarantee >80% threshold
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) (c98f5ff)
