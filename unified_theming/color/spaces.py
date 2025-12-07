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
        """Parse hex color (#RGB, #RRGGBB, #RRGGBBAA)."""
        h = hex_str.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return cls(r, g, b, a)

    def to_hex(self) -> str:
        """Convert to hex string."""
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
        """WCAG relative luminance."""
        lr, lg, lb = self.to_linear_rgb()
        return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb

    def to_oklch(self) -> "OKLCHColor":
        """Convert to OKLCH perceptual color space."""
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
        """Return copy with new lightness."""
        return OKLCHColor(max(0, min(1, l)), self.chroma, self.hue)

    def with_chroma(self, c: float) -> "OKLCHColor":
        """Return copy with new chroma."""
        return OKLCHColor(self.lightness, max(0, c), self.hue)

    def rotate_hue(self, degrees: float) -> "OKLCHColor":
        """Return copy with rotated hue."""
        return OKLCHColor(self.lightness, self.chroma, (self.hue + degrees) % 360)

    def to_rgb(self) -> Color:
        """Convert OKLCH back to sRGB."""
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
