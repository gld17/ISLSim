You are working on the ISLSim project at /share/guolidong-nfs/SeeSpace/ISLSim.

## Context

ISLSim is a lightweight FSO (free-space optical) inter-satellite link simulator. The project already has:

- `config.py`: TXConfig, RXConfig, ChannelConfig dataclasses; FSOConfig wrapper; `load_config_from_json()`
- `link_model.py`: Core physics (Friis path loss, EDFA SNR, M-QAM BER, modulation selection, bandwidth). Contains a very long Chinese docstring at the top (lines 1-32) explaining the "equal-rate heterogeneous" problem and modeling flow.
- `sweep.py`: CLI entry point for distance sweep with argparse.
- `point_test.py`: CLI entry point for single-distance test.
- `configs/google_constellation.json`: Example config.
- `README.md`: English README with config field table and project layout.

## Task

Implement the following changes. Do NOT modify:
- `config.py` dataclass definitions
- `configs/google_constellation.json`
- Core physics formulas in `link_model.py` (functions: `_antenna_gain_db`, `_path_loss_db`, `_edfa_snr`, `ber_mqam`, `_select_modulation`, `compute_link`, `sweep_distances`, `geomspace`, `sweep_range`, `print_table`, `save_csv`)
- Do NOT add new dependencies.

Do NOT include AC-1, AC-2, Milestone, Step, Phase, or any plan markers in code.

### 1. Create `validator.py` (new file at project root)

Implement a unified error-code system and config validation module.

```python
# validator.py requirements:

from enum import Enum, auto

class ErrorCode(Enum):
    INVALID_VALUE = auto()
    OUT_OF_RANGE = auto()
    MISSING_FIELD = auto()
    LINK_INFEASIBLE = auto()
    UNKNOWN = auto()

class ValidationError(Exception):
    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code.name}] {message}")
```

Implement `validate_config(config: FSOConfig) -> None` that validates:
- `config.tx_power_w > 0`
- `config.tx_aperture_m > 0`
- `config.wavelength_m > 0` AND `0.4e-6 <= config.wavelength_m <= 10e-6`
- `config.baud_rate_ghz > 0`
- `config.wdm_channels >= 1` and is int
- `0 <= config.fec_overhead < 1`
- `config.modulation_pool` is non-empty list, each item is `[order, label]` where `order` is a power of 2 and `order >= 4`
- `config.rx_aperture_m > 0`
- `config.preamp_gain_db >= 0`
- `config.preamp_nf_db >= 1`
- `0 < config.ber_threshold < 1`
- `config.terminal_cap_gbps is None or config.terminal_cap_gbps > 0`
- `config.link_margin_db >= 0`
- `0 < config.optical_efficiency <= 1`

Any failure raises `ValidationError` with appropriate `ErrorCode` and human-readable message.

Implement `pre_check_link_feasibility(config: FSOConfig) -> None`:
- Import `compute_link` from `link_model`.
- Run `compute_link(config, 100.0)`.
- If `result.feasible is False`, raise `ValidationError(ErrorCode.LINK_INFEASIBLE, "Link is infeasible even at 100 km with the given configuration")`.
- Also run `compute_link(config, 5000.0)` for informational purposes (do not raise on long-distance infeasibility).

### 2. Modify `sweep.py`

After `load_config_from_json(args.config)` and before `sweep_distances()`:
```python
from validator import validate_config, pre_check_link_feasibility, ValidationError

try:
    validate_config(cfg)
    pre_check_link_feasibility(cfg)
except ValidationError as e:
    import sys
    print(f"Config validation failed: {e.message}", file=sys.stderr)
    sys.exit(1)
```

### 3. Modify `point_test.py`

Same pattern: after `load_config_from_json(args.config)` and before `compute_link()`:
```python
from validator import validate_config, pre_check_link_feasibility, ValidationError

try:
    validate_config(config)
    pre_check_link_feasibility(config)
except ValidationError as e:
    import sys
    print(f"Config validation failed: {e.message}", file=sys.stderr)
    sys.exit(1)
```

### 4. Modify `link_model.py` `__main__` block

After `load_config_from_json(cfg_path)` and before `sweep_range()`:
```python
from validator import validate_config, pre_check_link_feasibility, ValidationError

try:
    validate_config(cfg)
    pre_check_link_feasibility(cfg)
except ValidationError as e:
    import sys
    print(f"Config validation failed: {e.message}", file=sys.stderr)
    sys.exit(1)
```

### 5. Trim `link_model.py` module-level docstring

The current `link_model.py` has a very long Chinese docstring from line 1 to ~32 explaining the "等速率异构" problem and modeling flow. Replace it with a concise module docstring, e.g.:
```python
"""Core FSO link-budget physics.

Physical engine for inter-satellite laser link simulation.
"""
```

Keep all function-level docstrings intact (especially `_antenna_gain_db`, `_path_loss_db`, `_edfa_snr`, `ber_mqam`, `_select_modulation`, `compute_link`).

### 6. Rewrite `README.md`

Restructure README into these sections:

1. **Title**: `# ISLSim — Inter-Satellite Laser Link Simulation`
2. **Overview** (1-2 sentences in English, then Chinese translation)
3. **Physical Model** (migrated from `link_model.py` module docstring):
   - 等速率异构问题 (equal-rate heterogeneous problem)
   - Modeling flow: `d(t) -> Pr(t) -> SNR(t) -> max M(t) -> BW(t)`
   - Brief description of Friis path loss, EDFA SNR, M-QAM BER selection
   - Keep references (Proakis, Agrawal, etc.)
4. **Installation**
5. **Usage**: `python link_model.py`, `python sweep.py`, `python point_test.py --distance-km 1000`
6. **Configuration**: Table for TXConfig, RXConfig, ChannelConfig fields (keep existing tables)
7. **Project Layout**: Each script described in ONE line only. Example:
   ```
   ├── config.py              # Configuration dataclasses
   ├── link_model.py          # Core link-budget physics
   ├── sweep.py               # Distance-sweep CLI
   ├── point_test.py          # Single-distance CLI
   ├── validator.py           # Config validation and pre-check
   ├── configs/               # JSON configuration files
   └── README.md              # This file
   ```
   - NO detailed explanation of internal formulas in this section.
   - NO redundant description of what each function does.

README should be primarily in Chinese with English section headers acceptable. Must contain the strings "物理模型" and "等速率异构".

### 7. Verification

After making all changes, run these checks from `/share/guolidong-nfs/SeeSpace/ISLSim`:

```bash
python -m py_compile config.py link_model.py sweep.py point_test.py validator.py
echo $?
```

Should output `0`.

```bash
python -c "from validator import ValidationError, ErrorCode; print(ErrorCode.INVALID_VALUE)"
```

Should output `ErrorCode.INVALID_VALUE`.

```bash
python -c "
from config import load_config_from_json
from validator import validate_config, pre_check_link_feasibility
cfg = load_config_from_json('configs/google_constellation.json')
validate_config(cfg)
pre_check_link_feasibility(cfg)
print('Validation passed')
"
```

Should output `Validation passed`.

```bash
python -c "
from config import load_config_from_json
from validator import validate_config, ValidationError
cfg = load_config_from_json('configs/google_constellation.json')
cfg.tx_power_w = -1
try:
    validate_config(cfg)
except ValidationError as e:
    print(f'Caught: {e.code.name}')
"
```

Should output `Caught: INVALID_VALUE`.

```bash
python sweep.py
```

Should output the same distance-bandwidth table as before (normal run).

```bash
python point_test.py --distance-km 1000
```

Should output a bandwidth number (not 0.0 for default config).

```bash
python link_model.py
```

Should output the same distance-bandwidth table as before.

```bash
grep -q "物理模型" README.md && grep -q "等速率异构" README.md && echo "README OK" || echo "README MISSING CONTENT"
```

Should output `README OK`.

```bash
head -n 30 link_model.py | grep -q "等速率异构" && echo "FAIL: docstring still there" || echo "OK: docstring trimmed"
```

Should output `OK: docstring trimmed`.

## Important Rules
- Do NOT modify `config.py`.
- Do NOT modify `configs/google_constellation.json`.
- Do NOT modify any physics formulas or function-level docstrings in `link_model.py`.
- Do NOT add new dependencies.
- Do NOT leave AC-/Milestone/Step/Phase markers in code.
- Use relative imports where the project already uses them (`from config import ...`, `from link_model import ...`). For `validator.py`, use `from config import FSOConfig` and `from link_model import compute_link`.
