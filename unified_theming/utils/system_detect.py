"""System detection utilities for cross-toolkit theming."""

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ToolkitEnvironment:
    """Detected toolkit environment information."""

    desktop: str  # gnome, kde, xfce, etc.
    has_gtk_apps: bool = True
    has_qt_apps: bool = False
    qt_packages_installed: List[str] = field(default_factory=list)
    qt_packages_missing: List[str] = field(default_factory=list)
    gtk_packages_missing: List[str] = field(default_factory=list)


# Required packages for Qt theming on GTK desktops
QT_ON_GTK_PACKAGES = {
    "debian": {
        "qt5": ["qt5-style-plugins", "qt5ct", "adwaita-qt"],
        "qt6": ["adwaita-qt6", "qt6ct"],
    },
    "fedora": {
        "qt5": ["adwaita-qt5", "qt5ct"],
        "qt6": ["adwaita-qt6", "qt6ct"],
    },
    "arch": {
        "qt5": ["adwaita-qt5", "qt5ct"],
        "qt6": ["adwaita-qt6", "qt6ct"],
    },
}

# Required packages for GTK theming on Qt/KDE desktops
GTK_ON_KDE_PACKAGES = {
    "debian": ["kde-gtk-config", "breeze-gtk-theme"],
    "fedora": ["kde-gtk-config", "breeze-gtk"],
    "arch": ["kde-gtk-config", "breeze-gtk"],
}


def detect_distro() -> str:
    """Detect Linux distribution family."""
    try:
        if Path("/etc/os-release").exists():
            content = Path("/etc/os-release").read_text()
            if "ubuntu" in content.lower() or "debian" in content.lower():
                return "debian"
            if "fedora" in content.lower() or "rhel" in content.lower():
                return "fedora"
            if "arch" in content.lower():
                return "arch"
    except Exception:
        pass
    return "debian"  # Default fallback


def detect_desktop() -> str:
    """Detect current desktop environment."""
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "gnome" in desktop:
        return "gnome"
    if "kde" in desktop or "plasma" in desktop:
        return "kde"
    if "xfce" in desktop:
        return "xfce"
    if "cinnamon" in desktop:
        return "cinnamon"
    return "unknown"


def check_package_installed(package: str, distro: str) -> bool:
    """Check if a package is installed."""
    try:
        if distro == "debian":
            result = subprocess.run(
                ["dpkg", "-s", package],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        elif distro == "fedora":
            result = subprocess.run(
                ["rpm", "-q", package],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        elif distro == "arch":
            result = subprocess.run(
                ["pacman", "-Q", package],
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
    except Exception:
        pass
    return False


def detect_qt_apps() -> bool:
    """Check if Qt applications are installed."""
    qt_indicators = [
        shutil.which("dolphin"),
        shutil.which("kate"),
        shutil.which("konsole"),
        shutil.which("kdenlive"),
        shutil.which("vlc"),
        shutil.which("virtualbox"),
        shutil.which("calibre"),
        Path("/usr/lib/x86_64-linux-gnu/libQt5Core.so.5").exists(),
        Path("/usr/lib/libQt5Core.so.5").exists(),
    ]
    return any(qt_indicators)


def detect_gtk_apps() -> bool:
    """Check if GTK applications are installed."""
    gtk_indicators = [
        shutil.which("nautilus"),
        shutil.which("gedit"),
        shutil.which("gnome-terminal"),
        shutil.which("firefox"),
        shutil.which("gimp"),
        Path("/usr/lib/x86_64-linux-gnu/libgtk-3.so.0").exists(),
        Path("/usr/lib/libgtk-3.so.0").exists(),
    ]
    return any(gtk_indicators)


def detect_environment() -> ToolkitEnvironment:
    """Detect full toolkit environment."""
    distro = detect_distro()
    desktop = detect_desktop()
    has_qt = detect_qt_apps()
    has_gtk = detect_gtk_apps()

    env = ToolkitEnvironment(
        desktop=desktop,
        has_gtk_apps=has_gtk,
        has_qt_apps=has_qt,
    )

    # Check Qt packages on GTK desktops
    if desktop in ("gnome", "xfce", "cinnamon") and has_qt:
        packages = QT_ON_GTK_PACKAGES.get(distro, QT_ON_GTK_PACKAGES["debian"])
        for pkg in packages.get("qt5", []) + packages.get("qt6", []):
            if check_package_installed(pkg, distro):
                env.qt_packages_installed.append(pkg)
            else:
                env.qt_packages_missing.append(pkg)

    # Check GTK packages on KDE
    if desktop == "kde" and has_gtk:
        packages = GTK_ON_KDE_PACKAGES.get(distro, GTK_ON_KDE_PACKAGES["debian"])
        for pkg in packages:
            if not check_package_installed(pkg, distro):
                env.gtk_packages_missing.append(pkg)

    return env


def get_install_command(packages: List[str], distro: Optional[str] = None) -> str:
    """Get package install command for distro."""
    if distro is None:
        distro = detect_distro()

    if distro == "debian":
        return f"sudo apt install -y {' '.join(packages)}"
    elif distro == "fedora":
        return f"sudo dnf install -y {' '.join(packages)}"
    elif distro == "arch":
        return f"sudo pacman -S --noconfirm {' '.join(packages)}"
    return f"# Install: {' '.join(packages)}"
