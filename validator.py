# -*- coding: utf-8 -*-
"""Configuration validation for ISLSim."""

from enum import Enum, auto
from typing import Any

from config import FSOConfig
from link_model import compute_link


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


def _is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


def _validate_positive(name: str, value: Any) -> None:
    if value <= 0:
        raise ValidationError(
            ErrorCode.INVALID_VALUE,
            f"{name} must be > 0, got {value}",
        )


def validate_config(config: FSOConfig) -> None:
    """Validate an FSO configuration before running link-budget computations."""
    _validate_positive("tx_power_w", config.tx_power_w)
    _validate_positive("tx_aperture_m", config.tx_aperture_m)

    _validate_positive("wavelength_m", config.wavelength_m)
    if not 0.4e-6 <= config.wavelength_m <= 10e-6:
        raise ValidationError(
            ErrorCode.OUT_OF_RANGE,
            "wavelength_m must be between 0.4e-6 and 10e-6 meters",
        )

    _validate_positive("baud_rate_ghz", config.baud_rate_ghz)

    if not isinstance(config.wdm_channels, int) or isinstance(config.wdm_channels, bool):
        raise ValidationError(
            ErrorCode.INVALID_VALUE,
            f"wdm_channels must be an int, got {type(config.wdm_channels).__name__}",
        )
    if config.wdm_channels < 1:
        raise ValidationError(
            ErrorCode.INVALID_VALUE,
            f"wdm_channels must be >= 1, got {config.wdm_channels}",
        )

    if not 0 <= config.fec_overhead < 1:
        raise ValidationError(
            ErrorCode.OUT_OF_RANGE,
            f"fec_overhead must satisfy 0 <= value < 1, got {config.fec_overhead}",
        )

    if not isinstance(config.modulation_pool, list) or not config.modulation_pool:
        raise ValidationError(
            ErrorCode.MISSING_FIELD,
            "modulation_pool must be a non-empty list",
        )
    for item in config.modulation_pool:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValidationError(
                ErrorCode.INVALID_VALUE,
                "each modulation_pool item must be [order, label]",
            )
        order, label = item
        if not isinstance(order, int) or isinstance(order, bool):
            raise ValidationError(
                ErrorCode.INVALID_VALUE,
                f"modulation order must be an int, got {order}",
            )
        if order < 4 or not _is_power_of_two(order):
            raise ValidationError(
                ErrorCode.INVALID_VALUE,
                f"modulation order must be a power of 2 and >= 4, got {order}",
            )
        if not isinstance(label, str) or not label:
            raise ValidationError(
                ErrorCode.INVALID_VALUE,
                f"modulation label must be a non-empty string, got {label}",
            )

    _validate_positive("rx_aperture_m", config.rx_aperture_m)

    if config.preamp_gain_db < 0:
        raise ValidationError(
            ErrorCode.INVALID_VALUE,
            f"preamp_gain_db must be >= 0, got {config.preamp_gain_db}",
        )
    if config.preamp_nf_db < 1:
        raise ValidationError(
            ErrorCode.INVALID_VALUE,
            f"preamp_nf_db must be >= 1, got {config.preamp_nf_db}",
        )
    if not 0 < config.ber_threshold < 1:
        raise ValidationError(
            ErrorCode.OUT_OF_RANGE,
            f"ber_threshold must satisfy 0 < value < 1, got {config.ber_threshold}",
        )
    if config.terminal_cap_gbps is not None and config.terminal_cap_gbps <= 0:
        raise ValidationError(
            ErrorCode.INVALID_VALUE,
            "terminal_cap_gbps must be None or > 0",
        )
    if config.link_margin_db < 0:
        raise ValidationError(
            ErrorCode.INVALID_VALUE,
            f"link_margin_db must be >= 0, got {config.link_margin_db}",
        )
    if not 0 < config.optical_efficiency <= 1:
        raise ValidationError(
            ErrorCode.OUT_OF_RANGE,
            "optical_efficiency must satisfy 0 < value <= 1",
        )


def pre_check_link_feasibility(config: FSOConfig) -> None:
    """Check short-range feasibility and exercise the long-range endpoint."""
    short_result = compute_link(config, 100.0)
    if not short_result.feasible:
        raise ValidationError(
            ErrorCode.LINK_INFEASIBLE,
            "Link is infeasible even at 100 km with the given configuration",
        )

    compute_link(config, 5000.0)
