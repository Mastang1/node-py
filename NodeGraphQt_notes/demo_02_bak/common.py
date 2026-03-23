from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LANG_ZH = "zh"
LANG_EN = "en"
SUPPORTED_LANGUAGES = (LANG_ZH, LANG_EN)

FLOW_IN = "flow_in"
FLOW_OUT = "flow_out"

BASE_DIR = Path(__file__).resolve().parent
NOTES_DIR = BASE_DIR.parent
WORKSPACE_ROOT = NOTES_DIR.parent
NODEGRAPHQT_ROOT = WORKSPACE_ROOT / "NodeGraphQt"

if str(NODEGRAPHQT_ROOT) not in sys.path:
    sys.path.insert(0, str(NODEGRAPHQT_ROOT))

GENERATED_DIR = BASE_DIR / "generated"
THEMES_DIR = BASE_DIR / "themes"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

DEFAULT_FLOW_PATH = GENERATED_DIR / "sample_flow.json"
DEFAULT_EXPORT_PATH = GENERATED_DIR / "sample_export.py"

THEME_DARK = "dark"
THEME_LIGHT = "light"
SUPPORTED_THEMES = (THEME_DARK, THEME_LIGHT)

_DEFAULT_NODE_ICON = "preview"
_CATEGORY_ICON_NAMES = {
    "signal generator": "signal",
    "digital pattern generator": "pattern",
    "multi serial card": "serial",
    "general flow": "branch",
    "general": "logic",
}


@dataclass(frozen=True)
class FieldSpec:
    name: str
    kind: str
    default: Any
    label_zh: str
    label_en: str
    tooltip_zh: str = ""
    tooltip_en: str = ""
    required: bool = False
    options: tuple[str, ...] = ()
    multiline: bool = False
    placeholder_zh: str = ""
    placeholder_en: str = ""
    minimum: float | int | None = None
    maximum: float | int | None = None

    def label(self, language: str) -> str:
        return self.label_zh if language == LANG_ZH else self.label_en

    def tooltip(self, language: str) -> str:
        return self.tooltip_zh if language == LANG_ZH else self.tooltip_en

    def placeholder(self, language: str) -> str:
        return self.placeholder_zh if language == LANG_ZH else self.placeholder_en


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_parent_directory(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def as_float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def as_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(float(value))


def as_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}
    return bool(value)


def cast_value(kind: str, value: Any) -> Any:
    if kind == "int":
        return as_int(value)
    if kind == "float":
        return as_float(value)
    if kind == "bool":
        return as_bool(value)
    return as_text(value) if kind in {"str", "enum", "multiline"} else value


def sanitize_identifier(value: Any, default: str = "value") -> str:
    text = as_text(value, default)
    chars: list[str] = []
    for char in text:
        if char.isalnum() or char == "_":
            chars.append(char)
        else:
            chars.append("_")
    identifier = "".join(chars).strip("_")
    if not identifier:
        identifier = default
    if identifier[0].isdigit():
        identifier = f"var_{identifier}"
    return identifier


def safe_session_key(value: Any, default: str = "session") -> str:
    return sanitize_identifier(value, default)


def pretty_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)


def normalize_data_type(value: str) -> str:
    normalized = as_text(value, "str").lower()
    aliases = {
        "object": "any",
        "mixed": "any",
        "integer": "int",
        "double": "float",
        "number": "float",
        "string": "str",
        "text": "str",
        "enum": "str",
    }
    return aliases.get(normalized, normalized)


def data_type_compatible(source_type: str, target_type: str) -> bool:
    source = normalize_data_type(source_type)
    target = normalize_data_type(target_type)
    if target == "any":
        return True
    if source == target:
        return True
    if target == "float" and source == "int":
        return True
    if target == "str" and source in {"str", "bool", "int", "float"}:
        return True
    if target == "bool" and source in {"bool", "int"}:
        return True
    return False


def resolve_node_icon_name(icon_name: str = "", category_en: str = "") -> str:
    icon = as_text(icon_name)
    if icon:
        return icon
    category_key = as_text(category_en).lower()
    return _CATEGORY_ICON_NAMES.get(category_key, _DEFAULT_NODE_ICON)


def resolve_node_icon_path(icon_name: str = "", category_en: str = "") -> str:
    return str(ICONS_DIR / f"{resolve_node_icon_name(icon_name, category_en)}.svg")
