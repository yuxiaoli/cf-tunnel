from rich.console import Console
from rich.theme import Theme

# Homebrew Neon Color Scheme
homebrew_neon_colors = {
    "background": "#050805",
    "foreground": "#E7FFE4",
    "cursor": "#11FF00",
    "selection": "#123D10",
    
    # Standard colors
    "black": "#0B120B",
    "red": "#FF4D4D",
    "green": "#11FF00",
    "yellow": "#D8FF3E",
    "blue": "#4DA6FF",
    "magenta": "#FF5CFF", # purple
    "cyan": "#44FFD2",
    "white": "#D9FFD6",
    
    # Bright colors
    "bright_black": "#4B684B",
    "bright_red": "#FF8080",
    "bright_green": "#72FF66",
    "bright_yellow": "#EAFF8A",
    "bright_blue": "#82C2FF",
    "bright_magenta": "#FF91FF", # brightPurple
    "bright_cyan": "#8AFFE5",
    "bright_white": "#FFFFFF",
}

# Define semantic roles using the Homebrew Neon colors
custom_theme = Theme({
    "info": homebrew_neon_colors["cyan"],
    "warning": homebrew_neon_colors["yellow"],
    "danger": homebrew_neon_colors["red"],
    "success": homebrew_neon_colors["green"],
    "primary": homebrew_neon_colors["blue"],
    "secondary": homebrew_neon_colors["magenta"],
    "muted": homebrew_neon_colors["bright_black"],
    "text": homebrew_neon_colors["foreground"],
})

# Export a pre-configured console using the Homebrew Neon theme
console = Console(theme=custom_theme)

def get_console() -> Console:
    """Return the configured Rich console instance."""
    return console
