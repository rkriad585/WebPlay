THEMES = {
    "dark": {
        "name": "Classic Dark",
        "mode": "dark",
        "palette": ["#0a0a0a", "#141414", "#1e1e1e", "#D71920", "#666666", "#e0e0e0", "#2a2a2a"],
    },
    "midnight_blue": {
        "name": "Midnight Blue",
        "mode": "dark",
        "palette": ["#0a0e1a", "#121826", "#1a2238", "#4a7cf7", "#5a6a8a", "#e8ecf1", "#222a42"],
    },
    "forest_night": {
        "name": "Forest Night",
        "mode": "dark",
        "palette": ["#0a1a0e", "#0f2415", "#183022", "#3d9e6a", "#5a7a6a", "#d0e8d8", "#223d2a"],
    },
    "violet_dusk": {
        "name": "Violet Dusk",
        "mode": "dark",
        "palette": ["#1a0a1e", "#221230", "#301a42", "#a855f7", "#7a6a8a", "#e8d0f0", "#3d2a50"],
    },
    "warm_ember": {
        "name": "Warm Ember",
        "mode": "dark",
        "palette": ["#1a100a", "#2a1a12", "#3d2818", "#f59e0b", "#8a7a5a", "#f0e0d0", "#4d3420"],
    },
    "cherry_red": {
        "name": "Cherry Red",
        "mode": "dark",
        "palette": ["#1a0e0e", "#2a1818", "#3d2424", "#ef4444", "#8a5a5a", "#f0d0d0", "#4d3030"],
    },
    "amoled": {
        "name": "Pure Black (AMOLED)",
        "mode": "dark",
        "palette": ["#000000", "#0a0a0a", "#141414", "#D71920", "#555555", "#cccccc", "#1e1e1e"],
    },
    "light_clean": {
        "name": "Light Clean",
        "mode": "light",
        "palette": ["#ffffff", "#f5f5f5", "#e8e8e8", "#D71920", "#888888", "#1a1a1a", "#d0d0d0"],
    },
    "ocean_breeze": {
        "name": "Ocean Breeze",
        "mode": "light",
        "palette": ["#f0f8ff", "#e0f0fa", "#d0e8f5", "#2b6cb0", "#6a8a9a", "#1a2a3a", "#c0ddf0"],
    },
    "sunny_day": {
        "name": "Sunny Day",
        "mode": "light",
        "palette": ["#fffaf0", "#fff5e8", "#fff0d8", "#d97706", "#9a8a7a", "#3a2a1a", "#ffe8c8"],
    },
    "mint_fresh": {
        "name": "Mint Fresh",
        "mode": "light",
        "palette": ["#f0fff4", "#e0fae8", "#d0f5dc", "#38a169", "#6a8a7a", "#1a2a22", "#c0f0d0"],
    },
    "lavender": {
        "name": "Lavender",
        "mode": "light",
        "palette": ["#faf5ff", "#f0e8fa", "#e8d8f5", "#8b5cf6", "#8a7a9a", "#2a1a3a", "#dcc8f0"],
    },
}

DEFAULT_THEME = "dark"


def resolve_theme(name):
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def get_theme_css(theme):
    p = theme["palette"]
    mode = theme.get("mode", "dark")
    bg_rgb = hex_to_rgb(p[0])
    surface_rgb = hex_to_rgb(p[1])
    elevated_rgb = hex_to_rgb(p[2])
    accent_rgb = hex_to_rgb(p[3])
    muted_rgb = hex_to_rgb(p[4]) if len(p) > 4 else hex_to_rgb(p[2])
    text_rgb = hex_to_rgb(p[5]) if len(p) > 5 else hex_to_rgb(p[3])
    hover_rgb = hex_to_rgb(p[6]) if len(p) > 6 else elevated_rgb

    if mode == "light":
        glass_opacity = "0.8"
        hover_opacity = "0.3"
        border_opacity = "0.3"
        glare_opacity = "0.4"
    else:
        glass_opacity = "0.6"
        hover_opacity = "0.5"
        border_opacity = "0.2"
        glare_opacity = "0.6"

    vars_list = [
        f"--th-bg: {p[0]};",
        f"--th-bg-rgb: {bg_rgb[0]}, {bg_rgb[1]}, {bg_rgb[2]};",
        f"--th-surface: {p[1]};",
        f"--th-surface-rgb: {surface_rgb[0]}, {surface_rgb[1]}, {surface_rgb[2]};",
        f"--th-elevated: {p[2]};",
        f"--th-elevated-rgb: {elevated_rgb[0]}, {elevated_rgb[1]}, {elevated_rgb[2]};",
        f"--th-hover-rgb: {hover_rgb[0]}, {hover_rgb[1]}, {hover_rgb[2]};",
        f"--th-accent: {p[3]};",
        f"--th-accent-rgb: {accent_rgb[0]}, {accent_rgb[1]}, {accent_rgb[2]};",
        f"--th-text: {p[5] if len(p) > 5 else p[3]};",
        f"--th-text-rgb: {text_rgb[0]}, {text_rgb[1]}, {text_rgb[2]};",
        f"--th-text-secondary: {p[4] if len(p) > 4 else p[2]};",
        f"--th-muted-rgb: {muted_rgb[0]}, {muted_rgb[1]}, {muted_rgb[2]};",
        f"--th-glass-bg: rgba({surface_rgb[0]}, {surface_rgb[1]}, {surface_rgb[2]}, {glass_opacity});",
        f"--th-glass-border: rgba({text_rgb[0]}, {text_rgb[1]}, {text_rgb[2]}, {border_opacity});",
        f"--th-border: rgba({elevated_rgb[0]}, {elevated_rgb[1]}, {elevated_rgb[2]}, 0.4);",
        f"--th-hover: rgba({hover_rgb[0]}, {hover_rgb[1]}, {hover_rgb[2]}, {hover_opacity});",
        f"--th-input-bg: rgba({elevated_rgb[0]}, {elevated_rgb[1]}, {elevated_rgb[2]}, 0.3);",
        f"--th-input-border: rgba({muted_rgb[0]}, {muted_rgb[1]}, {muted_rgb[2]}, 0.2);",
        f"--th-bg-glare: rgba({accent_rgb[0]}, {accent_rgb[1]}, {accent_rgb[2]}, {glare_opacity});",
        f"--th-shadow: rgba(0, 0, 0, 0.3);",
        f"--th-accent-shadow: rgba({accent_rgb[0]}, {accent_rgb[1]}, {accent_rgb[2]}, 0.3);",
    ]
    return "\n".join(vars_list)


def get_theme_list():
    return sorted(THEMES.keys())
