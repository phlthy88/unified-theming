"""
Validation utilities for Unified Theming Application.

This module provides utility functions for validating theme content,
including CSS syntax validation and color format validation.
"""
import re
from typing import List, Dict, Optional
from pathlib import Path

from ..core.exceptions import ColorValidationError
from ..core.types import ColorFormat, ColorPalette


def validate_css_syntax(css_content: str) -> List[str]:
    """
    Validate CSS syntax and return list of errors.
    
    Args:
        css_content: CSS content to validate
        
    Returns:
        List of validation error messages (empty if no errors)
    """
    errors = []
    
    try:
        # Basic CSS syntax validation - check for common issues
        lines = css_content.split('\n')
        
        # Track open braces for proper structure
        brace_count = 0
        in_comment = False
        
        for line_num, line in enumerate(lines, 1):
            # Handle multi-line comments
            if '/*' in line and '*/' not in line:
                in_comment = True
            elif '*/' in line and not in_comment:
                # Comment starts and ends on same line
                pass
            elif '*/' in line and in_comment:
                in_comment = False
                continue  # Skip the rest of this line after comment end
            
            if in_comment:
                continue
            
            # Count braces
            brace_count += line.count('{') - line.count('}')
            
            if brace_count < 0:
                errors.append(f"Line {line_num}: Extra closing brace without matching opening brace")
                brace_count = 0  # Reset to prevent cascading errors
            
            # Check for common syntax issues
            if ';;' in line:
                errors.append(f"Line {line_num}: Double semicolon detected")
            
            # Check for property without semicolon (not at end of block)
            if re.search(r'\w+\s*:\s*[^;]+{', line):
                errors.append(f"Line {line_num}: Property seems to be missing semicolon")
        
        if brace_count > 0:
            errors.append(f"CSS structure error: {brace_count} unclosed block{'s' if brace_count > 1 else ''}")
        
    except Exception as e:
        errors.append(f"CSS validation error: {str(e)}")
    
    return errors


def validate_color_format(color_value: str) -> bool:
    """
    Validate if a color value is in a valid format.
    
    Args:
        color_value: Color value string to validate
        
    Returns:
        True if color format is valid, False otherwise
    """
    # Normalize the color value
    color_value = color_value.strip().lower()
    
    # Regular expressions for different color formats
    patterns = {
        'hex': r'^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$',
        'hex_alpha': r'^#([0-9a-f]{4}|[0-9a-f]{8})$',
        'rgb': r'^rgb\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$',
        'rgba': r'^rgba\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*(0|1|0?\.\d+)\s*\)$',
        'hsl': r'^hsl\s*\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$',
        'hsla': r'^hsla\s*\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*,\s*(0|1|0?\.\d+)\s*\)$',
        'named': r'^(aqua|black|blue|fuchsia|gray|green|lime|maroon|navy|olive|purple|red|silver|teal|white|yellow|orange|pink|turquoise|violet|wheat|tan|plum|chocolate|salmon|coral|firebrick|indigo|gold|tomato|cyan|crimson|darkblue|darkcyan|darkgoldenrod|darkgray|darkgreen|darkkhaki|darkmagenta|darkolivegreen|darkorange|darkorchid|darkred|darksalmon|darkseagreen|darkslateblue|darkslategray|darkturquoise|darkviolet|deeppink|deepskyblue|dimgray|dodgerblue|forestgreen|goldenrod|gray|indianred|indigo|lavenderblush|lawngreen|lemonchiffon|lightcoral|lightcyan|lightgray|lightgreen|lightpink|magenta|mediumvioletred|olivedrab|orangered|orchid|palevioletred|peru|plum|rosybrown|royalblue|saddlebrown|salmon|sandybrown|seagreen|sienna|skyblue|slateblue|slategray|springgreen|steelblue|violet|yellowgreen|rebeccapurple)$'
    }
    
    for pattern in patterns.values():
        if re.match(pattern, color_value, re.IGNORECASE):
            return True
    
    return False


def normalize_color_format(color_value: str, target_format: ColorFormat) -> str:
    """
    Normalize a color value to a specific format.
    
    Args:
        color_value: Color value to normalize
        target_format: Target format
        
    Returns:
        Normalized color value in target format
        
    Raises:
        ColorValidationError: If color value is invalid or format conversion fails
    """
    if not validate_color_format(color_value):
        raise ColorValidationError("unknown", color_value, "Invalid color format")
    
    # For now, just return the color value as is
    # In a full implementation, we would convert between formats
    return color_value.strip()


def find_css_color_definitions(css_content: str) -> Dict[str, str]:
    """
    Find and extract CSS color definitions (@define-color).
    
    Args:
        css_content: CSS content to parse
        
    Returns:
        Dictionary mapping variable names to color values
    """
    # Remove CSS comments first
    css_clean = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Pattern to match @define-color statements
    pattern = r'@define-color\s+([\w-]+)\s+([^;]+);'
    
    color_definitions = {}
    for match in re.finditer(pattern, css_clean, re.IGNORECASE):
        var_name = match.group(1).strip()
        color_value = match.group(2).strip()
        color_definitions[var_name] = color_value
    
    return color_definitions


def validate_theme_structure(theme_path: Path) -> List[str]:
    """
    Validate the basic structure of a theme directory.
    
    Args:
        theme_path: Path to theme directory
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not theme_path.exists():
        errors.append(f"Theme directory does not exist: {theme_path}")
        return errors
    
    if not theme_path.is_dir():
        errors.append(f"Path is not a directory: {theme_path}")
        return errors
    
    # Check for at least one GTK version directory
    gtk_dirs = ["gtk-2.0", "gtk-3.0", "gtk-4.0"]
    has_gtk_support = any((theme_path / gtk_dir).exists() for gtk_dir in gtk_dirs)
    
    if not has_gtk_support:
        errors.append(f"Theme has no GTK support directories. Expected one of: {', '.join(gtk_dirs)}")
    
    return errors


def validate_color_palette(color_palette: ColorPalette) -> List[str]:
    """
    Validate a color palette for completeness and correctness.
    
    Args:
        color_palette: Dictionary of color names to values
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check for required colors that are commonly expected
    required_colors = [
        'theme_bg_color',
        'theme_fg_color',
        'theme_base_color',
        'theme_text_color',
        'theme_selected_bg_color',
        'theme_selected_fg_color'
    ]
    
    missing_required = [color for color in required_colors if color not in color_palette]
    if missing_required:
        errors.append(f"Missing required colors: {', '.join(missing_required)}")
    
    # Validate each color format
    for color_name, color_value in color_palette.items():
        if not validate_color_format(color_value):
            errors.append(f"Invalid format for color '{color_name}': {color_value}")
    
    return errors