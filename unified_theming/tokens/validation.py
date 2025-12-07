"""Token schema validation with accessibility checks."""

from dataclasses import dataclass, field
from typing import List

from ..color.wcag import contrast_ratio, meets_aa
from .schema import UniversalTokenSchema


@dataclass
class TokenValidationResult:
    """Result of token validation."""

    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate_tokens(schema: UniversalTokenSchema) -> TokenValidationResult:
    """
    Validate token schema for completeness and accessibility.

    Checks:
    - Content/surface contrast meets WCAG AA (4.5:1)
    - Secondary content contrast (min 3:1)
    - Accent visibility on surfaces
    - Inverse content/surface contrast
    - Error color visibility

    Args:
        schema: Token schema to validate.

    Returns:
        TokenValidationResult with errors and warnings.

    Examples:
        >>> from .defaults import create_light_tokens
        >>> schema = create_light_tokens()
        >>> result = validate_tokens(schema)
        >>> result.valid
        True
        >>> len(result.warnings)
        0
    """
    errors = []
    warnings = []

    # Check primary content on primary surface
    ratio = contrast_ratio(schema.content.primary, schema.surfaces.primary)
    if ratio < 4.5:
        errors.append(f"Content/surface contrast {ratio:.2f}:1 below WCAG AA (4.5:1)")
    elif ratio < 7.0:
        warnings.append(f"Content/surface contrast {ratio:.2f}:1 below WCAG AAA (7:1)")

    # Check secondary content
    sec_ratio = contrast_ratio(schema.content.secondary, schema.surfaces.primary)
    if sec_ratio < 3.0:
        errors.append(f"Secondary content contrast {sec_ratio:.2f}:1 too low (min 3:1)")

    # Check accent visibility
    accent_ratio = contrast_ratio(schema.accents.primary, schema.surfaces.primary)
    if accent_ratio < 3.0:
        warnings.append(
            f"Accent color contrast {accent_ratio:.2f}:1 may be hard to see"
        )

    # Check inverse content on inverse surface
    inv_ratio = contrast_ratio(schema.content.inverse, schema.surfaces.inverse)
    if inv_ratio < 4.5:
        warnings.append(f"Inverse content/surface contrast {inv_ratio:.2f}:1 below AA")

    # Check error color visibility
    err_ratio = contrast_ratio(schema.accents.error, schema.surfaces.primary)
    if err_ratio < 3.0:
        warnings.append(f"Error color contrast {err_ratio:.2f}:1 may be hard to see")

    return TokenValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
