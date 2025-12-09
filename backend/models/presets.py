import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Mapping


@dataclass(frozen=True)
class PresetConfig:
    target_L: float
    max_delta_L: float
    smooth_strength: float
    eye_smooth_strength: float
    glow_strength: float
    saturation_boost: float
    hydration_highlight: float
    wrinkle_soften: float
    detail_mix: float
    unsharp_amount: float
    unsharp_radius: float
    edge_enhance_mix: float


PRESET_CONFIGS: Dict[str, PresetConfig] = {
    "cerah": PresetConfig(
        target_L=165.0,
        max_delta_L=16.0,
        smooth_strength=0.24,
        eye_smooth_strength=0.18,
        glow_strength=0.10,
        saturation_boost=1.06,
        hydration_highlight=0.0,
        wrinkle_soften=0.0,
        detail_mix=0.14,
        unsharp_amount=0.06,
        unsharp_radius=1.2,
        edge_enhance_mix=0.65,
    ),
    "lembab": PresetConfig(
        target_L=158.0,
        max_delta_L=18.0,
        smooth_strength=0.47,
        eye_smooth_strength=0.40,
        glow_strength=0.18,
        saturation_boost=1.10,
        hydration_highlight=0.25,
        wrinkle_soften=0.0,
        detail_mix=0.10,
        unsharp_amount=0.05,
        unsharp_radius=1.0,
        edge_enhance_mix=0.55,
    ),
    "kerutan": PresetConfig(
        target_L=153.0,
        max_delta_L=12.0,
        smooth_strength=0.38,
        eye_smooth_strength=0.72,
        glow_strength=0.05,
        saturation_boost=1.02,
        hydration_highlight=0.07,
        wrinkle_soften=2.00,
        detail_mix=0.08,
        unsharp_amount=0.04,
        unsharp_radius=1.0,
        edge_enhance_mix=0.45,
    ),
}

VALID_PRESETS = set(PRESET_CONFIGS.keys())

OVERRIDES_PATH = Path(__file__).with_name("preset_overrides.json")


def as_dict_map() -> Dict[str, Dict[str, float]]:
    """Return presets as plain dict for JSON responses."""
    return {name: asdict(cfg) for name, cfg in PRESET_CONFIGS.items()}


def merge_config(preset: str, overrides: Mapping[str, float] | None = None) -> PresetConfig:
    """
    Merge a preset with optional overrides, returning a new PresetConfig.
    Unknown keys are ignored; missing keys fall back to base preset.
    """
    base = PRESET_CONFIGS.get(preset)
    if base is None:
        raise KeyError(f"Preset not found: {preset}")

    data = asdict(base)
    if overrides:
        for key, val in overrides.items():
            if key in data and val is not None:
                data[key] = float(val)
    return PresetConfig(**data)


def update_preset(preset: str, overrides: Mapping[str, float]) -> PresetConfig:
    """
    Update a preset in memory and persist it for future runs.
    """
    new_cfg = merge_config(preset, overrides)
    PRESET_CONFIGS[preset] = new_cfg
    save_overrides()
    return new_cfg


def save_overrides() -> None:
    """Persist the current presets to a JSON file."""
    try:
        payload = as_dict_map()
        OVERRIDES_PATH.write_text(json.dumps(payload, indent=2))
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to write preset overrides: {exc}")


def load_overrides() -> None:
    """Load persisted overrides, if any."""
    if not OVERRIDES_PATH.exists():
        return
    try:
        data = json.loads(OVERRIDES_PATH.read_text())
        for name, cfg in data.items():
            if name in PRESET_CONFIGS:
                PRESET_CONFIGS[name] = PresetConfig(**cfg)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to load preset overrides: {exc}")


# Load persisted tweaks on import so the main app uses the latest values.
load_overrides()

__all__ = [
    "PresetConfig",
    "PRESET_CONFIGS",
    "VALID_PRESETS",
    "as_dict_map",
    "merge_config",
    "update_preset",
    "save_overrides",
    "load_overrides",
]
