"""Color space implementations with perceptual OKLCH support."""

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Color:
    """Perceptually-aware color in sRGB space (0-255)."""

    r: int
    g: int
    b: int
    a: float = 1.0

    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        """Parse hex color string to Color object.

        Supports #RGB, #RRGGBB, and #RRGGBBAA formats.

        Args:
            hex_str: Hex color string starting with '#'.

        Returns:
            Color object with parsed RGB values.

        Examples:
            >>> Color.from_hex("#ff0000")
            Color(r=255, g=0, b=0, a=1.0)

            >>> Color.from_hex("#f00")
            Color(r=255, g=0, b=0, a=1.0)

            >>> Color.from_hex("#ff000080")
            Color(r=255, g=0, b=0, a=0.5019607843137255)
        """
        h = hex_str.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return cls(r, g, b, a)

    def to_hex(self) -> str:
        """Convert Color to hex string.

        Returns #RRGGBB for opaque colors, #RRGGBBAA for transparent.

        Returns:
            Hex color string.

        Examples:
            >>> Color(255, 0, 0).to_hex()
            '#ff0000'

            >>> Color(255, 0, 0, 0.5).to_hex()
            '#ff000080'
        """
        if self.a < 1.0:
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}{int(self.a * 255):02x}"
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_linear_rgb(self) -> Tuple[float, float, float]:
        """Convert sRGB to linear RGB (gamma correction)."""

        def linearize(c: int) -> float:
            v = c / 255
            return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

        return linearize(self.r), linearize(self.g), linearize(self.b)

    def luminance(self) -> float:
        """Calculate WCAG relative luminance (0.0 to 1.0).

        Returns:
            Luminance value where 0.0 is black, 1.0 is white.

        Examples:
            >>> Color(255, 255, 255).luminance()
            1.0

            >>> Color(0, 0, 0).luminance()
            0.0

            >>> Color(128, 128, 128).luminance()
            0.2126
        """
        lr, lg, lb = self.to_linear_rgb()
        return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb

    def to_oklch(self) -> "OKLCHColor":
        """Convert sRGB Color to OKLCH perceptual color space.

        Returns:
            OKLCHColor with lightness (0-1), chroma (0-0.4), hue (0-360).

        Examples:
            >>> Color(255, 0, 0).to_oklch()
            OKLCHColor(lightness=0.6279553606145516, chroma=0.25768330773615674, hue=29.23388519234262)
        """
        lr, lg, lb = self.to_linear_rgb()

        # Linear RGB → Oklab (via LMS)
        l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
        m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
        s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb

        l_ = math.copysign(abs(l) ** (1 / 3), l)
        m_ = math.copysign(abs(m) ** (1 / 3), m)
        s_ = math.copysign(abs(s) ** (1 / 3), s)

        L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
        a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
        b_val = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_

        # Oklab → OKLCH
        C = math.sqrt(a * a + b_val * b_val)
        H = math.degrees(math.atan2(b_val, a)) % 360

        return OKLCHColor(L, C, H)


@dataclass
class OKLCHColor:
    """Color in OKLCH perceptual space (lightness, chroma, hue)."""

    lightness: float  # 0-1
    chroma: float  # 0-~0.4
    hue: float  # 0-360

    def with_lightness(self, l: float) -> "OKLCHColor":
        """Return OKLCHColor copy with adjusted lightness.

        Args:
            l: New lightness value (0.0 to 1.0, clamped).

        Returns:
            OKLCHColor with updated lightness.

        Examples:
            >>> color = OKLCHColor(0.5, 0.2, 120)
            >>> color.with_lightness(0.8)
            OKLCHColor(lightness=0.8, chroma=0.2, hue=120)
        """
        return OKLCHColor(max(0, min(1, l)), self.chroma, self.hue)

    def with_chroma(self, c: float) -> "OKLCHColor":
        """Return OKLCHColor copy with adjusted chroma.

        Args:
            c: New chroma value (0.0 or greater).

        Returns:
            OKLCHColor with updated chroma.

        Examples:
            >>> color = OKLCHColor(0.5, 0.2, 120)
            >>> color.with_chroma(0.3)
            OKLCHColor(lightness=0.5, chroma=0.3, hue=120)
        """
        return OKLCHColor(self.lightness, max(0, c), self.hue)

    def rotate_hue(self, degrees: float) -> "OKLCHColor":
        """Return OKLCHColor copy with rotated hue.

        Args:
            degrees: Degrees to rotate hue (modulo 360).

        Returns:
            OKLCHColor with updated hue.

        Examples:
            >>> color = OKLCHColor(0.5, 0.2, 120)
            >>> color.rotate_hue(30)
            OKLCHColor(lightness=0.5, chroma=0.2, hue=150)
        """
        return OKLCHColor(self.lightness, self.chroma, (self.hue + degrees) % 360)

    def to_rgb(self) -> Color:
        """Convert OKLCHColor back to sRGB Color.

        Returns:
            Color object in sRGB space.

        Examples:
            >>> oklch = OKLCHColor(0.6279553606145516, 0.25768330773615674, 29.23388519234262)
            >>> oklch.to_rgb()
            Color(r=255, g=0, b=0, a=1.0)
        """
        # OKLCH → Oklab
        a = self.chroma * math.cos(math.radians(self.hue))
        b_val = self.chroma * math.sin(math.radians(self.hue))
        L = self.lightness

        # Oklab → Linear RGB (via LMS)
        l_ = L + 0.3963377774 * a + 0.2158037573 * b_val
        m_ = L - 0.1055613458 * a - 0.0638541728 * b_val
        s_ = L - 0.0894841775 * a - 1.2914855480 * b_val

        l = l_**3
        m = m_**3
        s = s_**3

        lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
        lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
        lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

        # Linear RGB → sRGB
        def gamma(c: float) -> int:
            if c <= 0.0031308:
                v = 12.92 * c
            else:
                v = 1.055 * (c ** (1 / 2.4)) - 0.055
            return max(0, min(255, int(v * 255 + 0.5)))

        return Color(gamma(lr), gamma(lg), gamma(lb))
