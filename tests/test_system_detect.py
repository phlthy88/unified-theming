"""Tests for system detection utilities."""

from unittest.mock import patch

from unified_theming.utils.system_detect import (
    ToolkitEnvironment,
    detect_desktop,
    detect_distro,
    get_install_command,
)


class TestSystemDetect:
    """Tests for system detection functions."""

    @patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "GNOME"})
    def test_detect_desktop_gnome(self):
        assert detect_desktop() == "gnome"

    @patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "KDE"})
    def test_detect_desktop_kde(self):
        assert detect_desktop() == "kde"

    @patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": ""})
    def test_detect_desktop_unknown(self):
        assert detect_desktop() == "unknown"

    def test_get_install_command_debian(self):
        cmd = get_install_command(["pkg1", "pkg2"], "debian")
        assert "apt install" in cmd
        assert "pkg1" in cmd
        assert "pkg2" in cmd

    def test_get_install_command_fedora(self):
        cmd = get_install_command(["pkg1"], "fedora")
        assert "dnf install" in cmd

    def test_get_install_command_arch(self):
        cmd = get_install_command(["pkg1"], "arch")
        assert "pacman -S" in cmd

    def test_toolkit_environment_dataclass(self):
        env = ToolkitEnvironment(
            desktop="gnome",
            has_qt_apps=True,
            qt_packages_missing=["qt5ct"],
        )
        assert env.desktop == "gnome"
        assert env.has_qt_apps is True
        assert "qt5ct" in env.qt_packages_missing
