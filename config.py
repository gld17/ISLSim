# -*- coding: utf-8 -*-
"""Configuration objects for the FSO inter-satellite link model."""

from dataclasses import asdict, dataclass, field
import json
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TXConfig:
    """Transmit-side hardware and waveform parameters."""

    tx_power_w: float
    tx_aperture_m: float
    wavelength_m: float = 1.55e-6
    baud_rate_ghz: float = 60.0
    wdm_channels: int = 2
    fec_overhead: float = 0.15
    dual_polarization: bool = True
    wdm_power_mode: str = "total_power_fixed"
    modulation_pool: List[Tuple[int, str]] = field(default_factory=lambda: [
        (16, "DP-16QAM"),
        (8, "DP-8QAM"),
        (4, "DP-QPSK"),
    ])


@dataclass
class RXConfig:
    """Receive-side terminal and pre-amplifier parameters."""

    rx_aperture_m: float
    preamp_gain_db: float
    preamp_nf_db: float
    ber_threshold: float
    terminal_cap_gbps: Optional[float]


@dataclass
class ChannelConfig:
    """Free-space optical channel parameters."""

    link_margin_db: float
    optical_efficiency: float


class FSOConfig:
    """Combined FSO configuration with legacy flat attribute access."""

    _TX_FIELDS = {
        "tx_power_w", "tx_aperture_m", "wavelength_m", "baud_rate_ghz",
        "wdm_channels", "fec_overhead", "dual_polarization",
        "wdm_power_mode", "modulation_pool",
    }
    _RX_FIELDS = {
        "rx_aperture_m", "preamp_gain_db", "preamp_nf_db",
        "ber_threshold", "terminal_cap_gbps",
    }
    _CHANNEL_FIELDS = {"link_margin_db", "optical_efficiency"}

    def __init__(
        self,
        tx: Optional[TXConfig] = None,
        rx: Optional[RXConfig] = None,
        channel: Optional[ChannelConfig] = None,
        **legacy_fields: Any,
    ) -> None:
        default_tx = TXConfig(tx_power_w=5.0, tx_aperture_m=0.10)
        default_rx = RXConfig(
            rx_aperture_m=0.10,
            preamp_gain_db=40.0,
            preamp_nf_db=7.5,
            ber_threshold=1e-3,
            terminal_cap_gbps=400.0,
        )
        default_channel = ChannelConfig(link_margin_db=7.0, optical_efficiency=0.7)

        self.tx = tx or default_tx
        self.rx = rx or default_rx
        self.channel = channel or default_channel

        unknown_fields = set(legacy_fields) - (
            self._TX_FIELDS | self._RX_FIELDS | self._CHANNEL_FIELDS
        )
        if unknown_fields:
            names = ", ".join(sorted(unknown_fields))
            raise TypeError(f"unknown FSOConfig field(s): {names}")

        for name, value in legacy_fields.items():
            setattr(self, name, value)

    def __getattr__(self, name: str) -> Any:
        if name in self._TX_FIELDS:
            return getattr(self.tx, name)
        if name in self._RX_FIELDS:
            return getattr(self.rx, name)
        if name in self._CHANNEL_FIELDS:
            return getattr(self.channel, name)
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"tx", "rx", "channel"}:
            object.__setattr__(self, name, value)
        elif name in self._TX_FIELDS:
            setattr(self.tx, name, value)
        elif name in self._RX_FIELDS:
            setattr(self.rx, name, value)
        elif name in self._CHANNEL_FIELDS:
            setattr(self.channel, name, value)
        else:
            object.__setattr__(self, name, value)


def _require_section(data: Dict[str, Any], section: str) -> Dict[str, Any]:
    value = data.get(section)
    if not isinstance(value, dict):
        raise ValueError(f"missing or invalid '{section}' config section")
    return value


def _require_fields(section_name: str, section: Dict[str, Any], fields: List[str]) -> None:
    missing = [name for name in fields if name not in section]
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"missing required field(s) in '{section_name}': {names}")


def _normalize_modulation_pool(value: Any) -> List[Tuple[int, str]]:
    if not isinstance(value, list):
        raise ValueError("tx.modulation_pool must be a list")
    normalized = []
    for item in value:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError("each modulation_pool item must be [order, label]")
        order, label = item
        normalized.append((int(order), str(label)))
    return normalized


def load_config_from_json(filepath: str) -> FSOConfig:
    """Load a nested JSON configuration file into an FSOConfig."""

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("top-level config must be a JSON object")

    tx_data = dict(_require_section(data, "tx"))
    rx_data = dict(_require_section(data, "rx"))
    channel_data = dict(_require_section(data, "channel"))

    _require_fields("tx", tx_data, [
        "tx_power_w", "tx_aperture_m", "baud_rate_ghz", "wdm_channels",
        "fec_overhead", "dual_polarization", "wdm_power_mode",
        "modulation_pool",
    ])
    _require_fields("rx", rx_data, [
        "rx_aperture_m", "preamp_gain_db", "preamp_nf_db",
        "ber_threshold", "terminal_cap_gbps",
    ])
    _require_fields("channel", channel_data, [
        "link_margin_db", "optical_efficiency",
    ])

    if "modulation_pool" in tx_data:
        tx_data["modulation_pool"] = _normalize_modulation_pool(
            tx_data["modulation_pool"]
        )

    return FSOConfig(
        tx=TXConfig(**tx_data),
        rx=RXConfig(**rx_data),
        channel=ChannelConfig(**channel_data),
    )


def config_to_dict(config: FSOConfig) -> dict:
    """Export an FSOConfig as a JSON-serializable nested dictionary."""

    return {
        "tx": asdict(config.tx),
        "rx": asdict(config.rx),
        "channel": asdict(config.channel),
    }
