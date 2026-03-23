from __future__ import annotations

from .common import ASSETS_DIR, GENERATED_DIR, ICONS_DIR, THEMES_DIR, ensure_directory


ICON_SPECS = {
    "new": {
        "primary": "#7C3AED",
        "secondary": "#C084FC",
        "glyph": """
  <path d="M7 4.5h5l3 3v8a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-10a1 1 0 0 1 1-1Z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M12 4.5v3h3" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M10 9.3v4.4M7.8 11.5h4.4" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
""",
    },
    "open": {
        "primary": "#0F9D58",
        "secondary": "#34D399",
        "glyph": """
  <path d="M4 7.5h4l1.3-1.8h6.7a1 1 0 0 1 1 1v1.2H4Z" fill="rgba(255,255,255,0.22)"/>
  <path d="M4 7.5h13l-1.5 7.2a1 1 0 0 1-1 .8H5.2a1 1 0 0 1-1-.8Z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
""",
    },
    "save": {
        "primary": "#F97316",
        "secondary": "#FDBA74",
        "glyph": """
  <path d="M6 4.5h7l2 2v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-10a1 1 0 0 1 1-1Z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M8 4.8v4h4v-4" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-linejoin="round"/>
  <rect x="7.8" y="11.4" width="4.5" height="2.5" rx="0.6" fill="#ffffff" fill-opacity="0.9"/>
""",
    },
    "save_as": {
        "primary": "#EF4444",
        "secondary": "#FCA5A5",
        "glyph": """
  <path d="M6 4.5h7l2 2v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-10a1 1 0 0 1 1-1Z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M8 4.8v4h4v-4" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-linejoin="round"/>
  <circle cx="14.4" cy="14.2" r="2.5" fill="#ffffff" fill-opacity="0.92"/>
  <path d="M14.4 12.9v2.6M13.1 14.2h2.6" fill="none" stroke="#EF4444" stroke-width="1.4" stroke-linecap="round"/>
""",
    },
    "undo": {
        "primary": "#475569",
        "secondary": "#94A3B8",
        "glyph": """
  <path d="M7.2 7.2 4.8 9.6l2.4 2.4" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M5.2 9.6h5.4a3.7 3.7 0 1 1 0 7.4H8.8" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>
""",
    },
    "redo": {
        "primary": "#0F766E",
        "secondary": "#5EEAD4",
        "glyph": """
  <path d="M12.8 7.2 15.2 9.6l-2.4 2.4" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M14.8 9.6H9.4a3.7 3.7 0 1 0 0 7.4h1.8" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>
""",
    },
    "layout": {
        "primary": "#7C3AED",
        "secondary": "#22D3EE",
        "glyph": """
  <rect x="4.5" y="4.8" width="4.2" height="3.6" rx="1" fill="#ffffff" fill-opacity="0.95"/>
  <rect x="11.3" y="8.2" width="4.2" height="3.6" rx="1" fill="#ffffff" fill-opacity="0.75"/>
  <rect x="4.5" y="11.8" width="4.2" height="3.6" rx="1" fill="#ffffff" fill-opacity="0.6"/>
  <path d="M8.7 6.6h1.8M12 8.2V7.4M8.7 13.6h1.8M12 11.8v1.8" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-linecap="round"/>
""",
    },
    "validate": {
        "primary": "#059669",
        "secondary": "#6EE7B7",
        "glyph": """
  <path d="M10 4.5 15 6.3v3.9c0 2.9-1.8 5.5-5 6.9-3.2-1.4-5-4-5-6.9V6.3Z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="m7.5 10.5 1.8 1.9 3.3-3.6" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "run": {
        "primary": "#16A34A",
        "secondary": "#4ADE80",
        "glyph": """
  <path d="M7 5.5 14.2 10 7 14.5Z" fill="#ffffff"/>
""",
    },
    "stop": {
        "primary": "#DC2626",
        "secondary": "#F87171",
        "glyph": """
  <rect x="6.2" y="6.2" width="7.6" height="7.6" rx="1.2" fill="#ffffff"/>
""",
    },
    "export": {
        "primary": "#2563EB",
        "secondary": "#60A5FA",
        "glyph": """
  <path d="M6 6.2h3.5" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M10 5.2 14.2 5.2 14.2 9.4" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M9.2 10.8 14.2 5.8" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M6 9.4v4a1 1 0 0 0 1 1h6.2a1 1 0 0 0 1-1V11" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "preview": {
        "primary": "#334155",
        "secondary": "#64748B",
        "glyph": """
  <path d="M3.8 10s2.3-3.7 6.2-3.7 6.2 3.7 6.2 3.7-2.3 3.7-6.2 3.7S3.8 10 3.8 10Z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <circle cx="10" cy="10" r="1.9" fill="#ffffff"/>
""",
    },
    "language": {
        "primary": "#0EA5E9",
        "secondary": "#67E8F9",
        "glyph": """
  <circle cx="10" cy="10" r="5.8" fill="none" stroke="#ffffff" stroke-width="1.3"/>
  <path d="M4.8 10h10.4M10 4.2a9 9 0 0 0 0 11.6M10 4.2a9 9 0 0 1 0 11.6" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round"/>
""",
    },
    "theme": {
        "primary": "#D97706",
        "secondary": "#FDE047",
        "glyph": """
  <path d="M11.5 4.6a5.2 5.2 0 1 0 3.9 8.8 5.4 5.4 0 1 1-3.9-8.8Z" fill="#ffffff"/>
  <path d="M10 2.8v1.4M10 15.8v1.4M17.2 10h-1.4M4.2 10H2.8M15.1 4.9 14.1 5.9M5.9 14.1 4.9 15.1" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round"/>
""",
    },
    "instruments": {
        "primary": "#7C2D12",
        "secondary": "#FB923C",
        "glyph": """
  <path d="M4.8 8.4h10.4M6.2 11h7.6M8 13.6h4" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>
  <rect x="4.2" y="5" width="11.6" height="10" rx="2" fill="none" stroke="#ffffff" stroke-width="1.4"/>
  <circle cx="6.6" cy="6.8" r="0.8" fill="#ffffff"/>
""",
    },
    "signal": {
        "primary": "#1D4ED8",
        "secondary": "#60A5FA",
        "glyph": """
  <path d="M4.2 10c1.1 0 1.1-3.4 2.2-3.4s1.1 6.8 2.2 6.8 1.1-6.8 2.2-6.8 1.1 3.4 2.2 3.4 1.1-1.7 2.2-1.7" fill="none" stroke="#ffffff" stroke-width="1.45" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "connect": {
        "primary": "#0F766E",
        "secondary": "#2DD4BF",
        "glyph": """
  <path d="M7 7.2h2.2M10.8 7.2h2.2M7 12.8h2.2M10.8 12.8h2.2" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M5.2 9.2a2 2 0 0 1 0-4h1.6M14.8 10.8a2 2 0 0 1 0 4h-1.6M6.8 14.8H5.2a2 2 0 0 1 0-4M13.2 5.2h1.6a2 2 0 1 1 0 4" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "identity": {
        "primary": "#1D4ED8",
        "secondary": "#93C5FD",
        "glyph": """
  <rect x="4.2" y="5.2" width="11.6" height="9.6" rx="1.6" fill="none" stroke="#ffffff" stroke-width="1.4"/>
  <circle cx="7.1" cy="8.3" r="1.1" fill="#ffffff"/>
  <path d="M9.4 8.2h4.2M6.2 11.3h7.2" fill="none" stroke="#ffffff" stroke-width="1.35" stroke-linecap="round"/>
""",
    },
    "test": {
        "primary": "#059669",
        "secondary": "#6EE7B7",
        "glyph": """
  <path d="M6.2 5.4h7.6v2.2H6.2zM7.2 7.6v4.2a2.8 2.8 0 1 0 5.6 0V7.6" fill="none" stroke="#ffffff" stroke-width="1.35" stroke-linejoin="round"/>
  <path d="m8.2 10.4 1.3 1.4 2.3-2.5" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "waveform": {
        "primary": "#2563EB",
        "secondary": "#7DD3FC",
        "glyph": """
  <path d="M4.2 10c1 0 1-3 2-3s1 6 2 6 1-6 2-6 1 3 2 3 1-1.5 2-1.5" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="4.4" y="4.8" width="11.2" height="10.4" rx="2" fill="none" stroke="#ffffff" stroke-opacity="0.45" stroke-width="1"/>
""",
    },
    "power": {
        "primary": "#DC2626",
        "secondary": "#FCA5A5",
        "glyph": """
  <path d="M10 4.8v4.1" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round"/>
  <path d="M13.6 6.4a4.8 4.8 0 1 1-7.2 0" fill="none" stroke="#ffffff" stroke-width="1.45" stroke-linecap="round"/>
""",
    },
    "timing": {
        "primary": "#7C3AED",
        "secondary": "#C4B5FD",
        "glyph": """
  <path d="M5 12.8V7.2h2.4v5.6h2.1V5.6h2.3v7.2h2.2V8.8H15" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/>
""",
    },
    "pattern_load": {
        "primary": "#7C3AED",
        "secondary": "#E879F9",
        "glyph": """
  <path d="M5.2 6.2h9.6v7.6H5.2z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M7 8.2h6M7 10.2h4.2M10 4.6v2.2M8.6 5.8h2.8" fill="none" stroke="#ffffff" stroke-width="1.35" stroke-linecap="round"/>
""",
    },
    "pattern": {
        "primary": "#7C3AED",
        "secondary": "#C084FC",
        "glyph": """
  <rect x="4.2" y="5.4" width="2.2" height="9.2" rx="0.8" fill="#ffffff" fill-opacity="0.95"/>
  <rect x="8.9" y="8.4" width="2.2" height="6.2" rx="0.8" fill="#ffffff" fill-opacity="0.78"/>
  <rect x="13.6" y="4.2" width="2.2" height="10.4" rx="0.8" fill="#ffffff" fill-opacity="0.62"/>
""",
    },
    "serial": {
        "primary": "#0F766E",
        "secondary": "#5EEAD4",
        "glyph": """
  <path d="M5 6.2h10v7.6H5z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M7 8.2h1M9.6 8.2h1M12.2 8.2h1M7 11.2h6.2" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-linecap="round"/>
""",
    },
    "port": {
        "primary": "#0F766E",
        "secondary": "#67E8F9",
        "glyph": """
  <rect x="5" y="5.4" width="10" height="9.2" rx="2" fill="none" stroke="#ffffff" stroke-width="1.4"/>
  <path d="M7.2 8.2h5.6M7.2 11.2h2.8M13.6 8.2h0M13.6 11.2h0" fill="none" stroke="#ffffff" stroke-width="1.35" stroke-linecap="round"/>
""",
    },
    "branch": {
        "primary": "#9333EA",
        "secondary": "#E879F9",
        "glyph": """
  <path d="M6 5.6v8.8M6 8h5.5M11.5 8l2.5-2.4M11.5 8l2.5 2.4M6 12h5.5M11.5 12l2.5-2.4M11.5 12l2.5 2.4" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "loop": {
        "primary": "#B45309",
        "secondary": "#F59E0B",
        "glyph": """
  <path d="M14.6 8.1A4.8 4.8 0 1 0 15 10h-2.2M14.2 5.8v3h-3" fill="none" stroke="#ffffff" stroke-width="1.45" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "logic": {
        "primary": "#4F46E5",
        "secondary": "#818CF8",
        "glyph": """
  <path d="M5 6.2h5.5a3.8 3.8 0 1 1 0 7.6H5z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <circle cx="14.2" cy="10" r="1.3" fill="#ffffff"/>
""",
    },
    "compare": {
        "primary": "#0EA5E9",
        "secondary": "#67E8F9",
        "glyph": """
  <path d="M5.2 7.2 8.4 10 5.2 12.8M14.8 7.2 11.6 10l3.2 2.8" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "variable": {
        "primary": "#2563EB",
        "secondary": "#93C5FD",
        "glyph": """
  <path d="M6 5.8 10 14.2 14 5.8" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M8.2 11.2h3.6" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>
""",
    },
    "bool": {
        "primary": "#16A34A",
        "secondary": "#86EFAC",
        "glyph": """
  <circle cx="10" cy="10" r="5.2" fill="none" stroke="#ffffff" stroke-width="1.4"/>
  <path d="m7.4 10 1.6 1.7 3.5-3.7" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
""",
    },
    "number": {
        "primary": "#0369A1",
        "secondary": "#7DD3FC",
        "glyph": """
  <path d="M7.2 5.4 6 14.6M12.4 5.4l-1.2 9.2M5.4 8.4h8.8M4.8 11.6h8.8" fill="none" stroke="#ffffff" stroke-width="1.35" stroke-linecap="round"/>
""",
    },
    "text": {
        "primary": "#BE185D",
        "secondary": "#FDA4AF",
        "glyph": """
  <path d="M5.2 6h9.6M10 6v8M7.4 14h5.2" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
""",
    },
    "read": {
        "primary": "#0284C7",
        "secondary": "#7DD3FC",
        "glyph": """
  <path d="M4.6 10s2.1-3.2 5.4-3.2 5.4 3.2 5.4 3.2-2.1 3.2-5.4 3.2S4.6 10 4.6 10Z" fill="none" stroke="#ffffff" stroke-width="1.35" stroke-linejoin="round"/>
  <circle cx="10" cy="10" r="1.4" fill="#ffffff"/>
  <path d="M14.4 5.6v4.2M12.3 7.7h4.2" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round"/>
""",
    },
    "write": {
        "primary": "#EA580C",
        "secondary": "#FDBA74",
        "glyph": """
  <path d="M5.2 13.8 6 11l5.4-5.4 2.8 2.8-5.4 5.4z" fill="none" stroke="#ffffff" stroke-width="1.35" stroke-linejoin="round"/>
  <path d="m10.9 6.1 2.8 2.8M5.1 13.9l2.2-.6" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-linecap="round"/>
""",
    },
    "constant": {
        "primary": "#7C3AED",
        "secondary": "#DDD6FE",
        "glyph": """
  <path d="M6 6.2h8v7.6H6z" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linejoin="round"/>
  <path d="M8 8.8h4M8 11.2h4" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>
""",
    },
    "center": {
        "primary": "#0F766E",
        "secondary": "#2DD4BF",
        "glyph": """
  <path d="M5.2 8V5.2H8M12 5.2h2.8V8M14.8 12v2.8H12M8 14.8H5.2V12" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="10" cy="10" r="1.5" fill="#ffffff"/>
""",
    },
    "row": {
        "primary": "#0369A1",
        "secondary": "#38BDF8",
        "glyph": """
  <rect x="4" y="8" width="3.2" height="4" rx="1" fill="#ffffff" fill-opacity="0.95"/>
  <rect x="8.4" y="8" width="3.2" height="4" rx="1" fill="#ffffff" fill-opacity="0.78"/>
  <rect x="12.8" y="8" width="3.2" height="4" rx="1" fill="#ffffff" fill-opacity="0.62"/>
""",
    },
    "column": {
        "primary": "#6D28D9",
        "secondary": "#A78BFA",
        "glyph": """
  <rect x="8" y="4" width="4" height="3.2" rx="1" fill="#ffffff" fill-opacity="0.95"/>
  <rect x="8" y="8.4" width="4" height="3.2" rx="1" fill="#ffffff" fill-opacity="0.78"/>
  <rect x="8" y="12.8" width="4" height="3.2" rx="1" fill="#ffffff" fill-opacity="0.62"/>
""",
    },
    "debug_run": {
        "primary": "#7C2D12",
        "secondary": "#F97316",
        "glyph": """
  <ellipse cx="8.5" cy="9.5" rx="4.2" ry="3.2" fill="none" stroke="#ffffff" stroke-width="1.3"/>
  <path d="M6.2 7.2 7.8 5.6 9.4 7.2" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round"/>
  <circle cx="7.4" cy="9.3" r="0.55" fill="#ffffff"/>
  <circle cx="9.6" cy="9.3" r="0.55" fill="#ffffff"/>
  <path d="M7.4 11.2c.8.6 1.8.6 2.6 0" fill="none" stroke="#ffffff" stroke-width="1.1" stroke-linecap="round"/>
""",
    },
    "debug_step": {
        "primary": "#1D4ED8",
        "secondary": "#38BDF8",
        "glyph": """
  <path d="M5 6.5h6.5v7H5z" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-linejoin="round"/>
  <path d="M7.2 8.8h2.2M7.2 11h2.2" fill="none" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round"/>
  <path d="M13.2 7.5v5l2.2-2.5z" fill="#ffffff" fill-opacity="0.92"/>
""",
    },
    "debug_continue": {
        "primary": "#047857",
        "secondary": "#34D399",
        "glyph": """
  <path d="M5.5 6.2v7.6l6-3.8z" fill="#ffffff" fill-opacity="0.95"/>
  <path d="M13.5 6.2v7.6l4-2.2v-3.2z" fill="#ffffff" fill-opacity="0.75"/>
""",
    },
    "debug_stop": {
        "primary": "#B91C1C",
        "secondary": "#F87171",
        "glyph": """
  <rect x="5.5" y="5.5" width="9" height="9" rx="1.8" fill="#ffffff" fill-opacity="0.92"/>
""",
    },
    "breakpoint": {
        "primary": "#A16207",
        "secondary": "#FACC15",
        "glyph": """
  <circle cx="10" cy="10" r="5.2" fill="#ffffff" fill-opacity="0.95"/>
  <circle cx="10" cy="10" r="2.4" fill="#A16207"/>
""",
    },
    "code_snippet": {
        "primary": "#4338CA",
        "secondary": "#818CF8",
        "glyph": """
  <path d="M6.2 7.2 4.5 9 6.2 10.8M13.8 7.2 15.5 9 13.8 10.8" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M9.2 6.3l1.6 5.4" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-linecap="round"/>
""",
    },
}


def _svg_template(name: str, primary: str, secondary: str, glyph: str) -> str:
    gradient_id = f"grad_{name}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">
  <defs>
    <linearGradient id="{gradient_id}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{primary}"/>
      <stop offset="100%" stop-color="{secondary}"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="18" height="18" rx="5" fill="url(#{gradient_id})"/>
  <rect x="1" y="1" width="18" height="18" rx="5" fill="none" stroke="#ffffff" stroke-opacity="0.18"/>
  <path d="M4.2 4.2h11.6" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1"/>
{glyph}</svg>
"""


def ensure_svg_icons() -> None:
    ensure_directory(ASSETS_DIR)
    ensure_directory(ICONS_DIR)
    for name, spec in ICON_SPECS.items():
        path = ICONS_DIR / f"{name}.svg"
        path.write_text(
            _svg_template(name, spec["primary"], spec["secondary"], spec["glyph"]),
            encoding="utf-8",
        )


def ensure_runtime_directories() -> None:
    ensure_directory(GENERATED_DIR)
    ensure_directory(THEMES_DIR)


def ensure_assets() -> None:
    ensure_runtime_directories()
    ensure_svg_icons()
