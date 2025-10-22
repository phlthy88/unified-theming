"""
Configuration manager for Unified Theming Application.

This module implements the ConfigManager which handles configuration
backup, restoration, and state persistence.
"""
import json
import shutil
import tarfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from ..utils.logging_config import get_logger
from ..utils.file import ensure_directory_exists
from ..core.types import Backup, Toolkit
from ..core.exceptions import (
    BackupError, BackupNotFoundError, RollbackError, ConfigurationError
)

logger = get_logger(__name__)

class ConfigManager:
    """
    Manager for configuration backup, restoration, and state persistence.
    
    This class handles backing up current configurations before theme changes,
    restoring configurations when needed, and managing backup lifecycle.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to store backups. Defaults to ~/.config/unified-theming/backups
        """
        self.config_dir = config_path or (Path.home() / ".config" / "unified-theming")
        self.backup_dir = self.config_dir / "backups"
        self.metadata_file = "metadata.json"
        
        # Ensure backup directory exists
        ensure_directory_exists(self.backup_dir)
        
        logger.info(f"ConfigManager initialized with backup directory: {self.backup_dir}")

    def backup_current_state(self) -> str:
        """
        Create backup of current configuration.
        
        This method creates a backup of all relevant configuration files
        before applying a new theme, allowing for restoration if needed.
        
        Returns:
            Backup ID (timestamp-based identifier)
            
        Raises:
            BackupError: If backup creation fails
        """
        # Use microsecond precision timestamp to ensure unique backup IDs even when called rapidly
        # Use microsecond precision timestamp for unique backup ID
        unique_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        # Use standard timestamp format for metadata
        metadata_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        theme_name = "current"  # We'll determine actual theme name in a real implementation
        backup_id = f"backup_{unique_timestamp}_{theme_name}"
        backup_path = self.backup_dir / backup_id
        
        logger.info(f"Creating backup: {backup_id}")
        
        try:
            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Identify files to backup based on common theme configuration locations
            files_to_backup = self._get_config_files_to_backup()
            
            # Backup each file/directory
            backup_metadata = {
                "backup_id": backup_id,
                "timestamp": metadata_timestamp,
                "theme_name": theme_name,
                "toolkits": [],
                "files": {},
                "metadata": {}
            }
            
            for toolkit, paths in files_to_backup.items():
                toolkit_files = {}
                for path in paths:
                    if path.exists():
                        # Create relative path for storage in metadata
                        relative_path = path.name if path.is_file() else path.name
                        backup_file_path = backup_path / relative_path
                        
                        if path.is_file():
                            shutil.copy2(path, backup_file_path)
                            toolkit_files[str(path)] = str(relative_path)
                        elif path.is_dir():
                            # For directories, create a tar archive
                            archive_path = backup_path / f"{path.name}.tar.gz"
                            with tarfile.open(archive_path, "w:gz") as tar:
                                tar.add(path, arcname=path.name)
                            toolkit_files[str(path)] = str(archive_path.name)
                
                if toolkit_files:
                    backup_metadata["files"][toolkit.value] = toolkit_files
                    backup_metadata["toolkits"].append(toolkit.value)
            
            # Write metadata file
            metadata_path = backup_path / self.metadata_file
            with open(metadata_path, 'w') as f:
                json.dump(backup_metadata, f, indent=2, default=str)
            
            # Clean up old backups (keep only recent ones)
            self._cleanup_old_backups()
            
            logger.info(f"Backup created successfully: {backup_path}")
            return backup_id
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise BackupError(
                f"Failed to create backup: {str(e)}",
                backup_path=backup_path
            )

    def _get_config_files_to_backup(self) -> Dict[Toolkit, List[Path]]:
        """
        Get list of configuration files that should be backed up.
        
        Returns:
            Dictionary mapping toolkits to lists of files/directories
        """
        config_files = {}
        
        # GTK configurations
        gtk_files = []
        gtk4_dir = Path.home() / ".config" / "gtk-4.0"
        if gtk4_dir.exists():
            gtk_files.append(gtk4_dir)
        
        gtk3_dir = Path.home() / ".config" / "gtk-3.0"
        if gtk3_dir.exists():
            gtk_files.append(gtk3_dir)
        
        gtk2_file = Path.home() / ".gtkrc-2.0"
        if gtk2_file.exists():
            gtk_files.append(gtk2_file)
        
        if gtk_files:
            config_files[Toolkit.GTK3] = gtk_files  # Using GTK3 as parent toolkit
        
        # Qt configurations
        qt_files = []
        kdeglobals_file = Path.home() / ".config" / "kdeglobals"
        if kdeglobals_file.exists():
            qt_files.append(kdeglobals_file)
        
        kvantum_dir = Path.home() / ".config" / "Kvantum"
        if kvantum_dir.exists():
            qt_files.append(kvantum_dir)
        
        if qt_files:
            config_files[Toolkit.QT5] = qt_files  # Using QT5 as parent toolkit
        
        # Flatpak configurations
        flatpak_files = []
        flatpak_config = Path.home() / ".config" / "flatpak/overrides"
        if flatpak_config.exists():
            flatpak_files.append(flatpak_config)
        
        if flatpak_files:
            config_files[Toolkit.FLATPAK] = flatpak_files
        
        # Snap configurations (if any specific configs exist)
        snap_files = []
        # No standard snap configuration file for theming, but we could add if needed
        if snap_files:
            config_files[Toolkit.SNAP] = snap_files
        
        return config_files

    def restore_backup(self, backup_id: str) -> bool:
        """
        Restore previous configuration from backup.
        
        Args:
            backup_id: ID of backup to restore
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            BackupNotFoundError: If backup doesn't exist
            RollbackError: If restoration fails
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            raise BackupNotFoundError(backup_id, backup_dir=self.backup_dir)
        
        logger.info(f"Restoring backup: {backup_id}")
        
        try:
            # Load metadata
            metadata_path = backup_path / self.metadata_file
            if not metadata_path.exists():
                raise RollbackError(
                    f"Backup metadata not found: {metadata_path}",
                    backup_id=backup_id
                )
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Restore each file/directory
            for toolkit, files in metadata.get("files", {}).items():
                for original_path_str, backup_path_str in files.items():
                    original_path = Path(original_path_str)
                    backup_file_path = backup_path / backup_path_str
                    
                    if not backup_file_path.exists():
                        logger.warning(f"Backup file not found: {backup_file_path}")
                        continue
                    
                    # Create parent directory if needed
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # If backup is a tar archive (for directories)
                    if backup_file_path.suffixes and backup_file_path.suffixes[-1] == ".gz":
                        with tarfile.open(backup_file_path, "r:gz") as tar:
                            # Extract to parent directory of the original
                            tar.extractall(path=original_path.parent)
                    else:
                        # Regular file copy
                        shutil.copy2(backup_file_path, original_path)
            
            logger.info(f"Backup restored successfully: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise RollbackError(
                f"Failed to restore backup {backup_id}: {str(e)}",
                backup_id=backup_id,
                partial_rollback=False
            )

    def get_backups(self) -> List[Backup]:
        """
        List available backups.
        
        Returns:
            List of Backup objects
        """
        backups = []
        
        for item in self.backup_dir.iterdir():
            if item.is_dir() and item.name.startswith("backup_"):
                try:
                    metadata_path = item / self.metadata_file
                    if metadata_path.exists():
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        
                        backup = Backup(
                            backup_id=metadata["backup_id"],
                            timestamp=datetime.fromisoformat(metadata["timestamp"]),
                            theme_name=metadata["theme_name"],
                            backup_path=item,
                            toolkits=[Toolkit(tk) for tk in metadata.get("toolkits", [])],
                            metadata=metadata.get("metadata", {})
                        )
                        backups.append(backup)
                        
                except Exception as e:
                    logger.warning(f"Failed to load metadata for backup {item.name}: {e}")
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups

    def _cleanup_old_backups(self) -> None:
        """
        Remove old backups, keeping only the most recent ones.
        """
        keep_count = 10  # Keep only the 10 most recent backups
        
        backups = self.get_backups()
        if len(backups) > keep_count:
            old_backups = backups[keep_count:]
            
            for backup in old_backups:
                try:
                    shutil.rmtree(backup.backup_path)
                    logger.debug(f"Removed old backup: {backup.backup_id}")
                except Exception as e:
                    logger.warning(f"Failed to remove old backup {backup.backup_id}: {e}")

    def get_current_state(self) -> Dict[str, str]:
        """
        Get current theme state for all toolkits.
        
        Returns:
            Dictionary mapping toolkit names to current theme names
        """
        # This is a basic implementation
        # In a full implementation, this would check actual system configuration
        state = {}
        
        # Check GTK theme
        try:
            import subprocess
            result = subprocess.run([
                "gsettings", "get", 
                "org.gnome.desktop.interface", 
                "gtk-theme"
            ], capture_output=True, text=True, check=True)
            
            theme_name = result.stdout.strip().strip("'\"")
            state["gtk"] = theme_name
        except:
            state["gtk"] = "default"
        
        # For Qt, check kdeglobals existence
        kdeglobals_path = Path.home() / ".config" / "kdeglobals"
        if kdeglobals_path.exists():
            state["qt"] = "custom"  # Would need to parse kdeglobals to get actual theme
        else:
            state["qt"] = "default"
        
        return state

    def save_config(self, config_data: Dict[str, any]) -> None:
        """
        Save configuration data to the config file.
        
        Args:
            config_data: Dictionary containing configuration data to save
        """
        config_file = self.config_dir / "config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")

    def load_config(self) -> Dict[str, any]:
        """
        Load configuration data from the config file.
        
        Returns:
            Dictionary containing configuration data, or empty dict if file doesn't exist
        """
        config_file = self.config_dir / "config.json"
        if not config_file.exists():
            logger.debug(f"Configuration file does not exist: {config_file}")
            return {}
        
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            return config_data
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")

    def get_config_value(self, key: str, default=None):
        """
        Get a specific configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            Value of the configuration key or default if not found
        """
        config = self.load_config()
        return config.get(key, default)

    def get_backup_info(self, backup_id: str) -> Backup:
        """
        Get detailed information about a specific backup.
        
        Args:
            backup_id: ID of the backup to get info for
            
        Returns:
            Backup object with detailed information
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            raise BackupNotFoundError(backup_id, backup_dir=self.backup_dir)
        
        metadata_path = backup_path / self.metadata_file
        if not metadata_path.exists():
            raise BackupError(f"Backup metadata not found: {metadata_path}", backup_path=backup_path)
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            return Backup(
                backup_id=metadata["backup_id"],
                timestamp=datetime.fromisoformat(metadata["timestamp"]),
                theme_name=metadata["theme_name"],
                backup_path=backup_path,
                toolkits=[Toolkit(tk) for tk in metadata.get("toolkits", [])],
                metadata=metadata.get("metadata", {})
            )
        except Exception as e:
            logger.error(f"Failed to load backup info: {e}")
            raise BackupError(f"Failed to load backup info for {backup_id}: {str(e)}", backup_path=backup_path)

    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a specific backup.
        
        Args:
            backup_id: ID of the backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            raise BackupNotFoundError(backup_id, backup_dir=self.backup_dir)
        
        try:
            shutil.rmtree(backup_path)
            logger.info(f"Backup deleted: {backup_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            raise BackupError(f"Failed to delete backup {backup_id}: {str(e)}", backup_path=backup_path)

    def prune_old_backups(self, keep: int = 10) -> int:
        """
        Remove old backups, keeping only the most recent ones.
        
        Args:
            keep: Number of recent backups to keep
            
        Returns:
            Number of backups deleted
        """
        backups = self.get_backups()
        if len(backups) <= keep:
            return 0  # No backups to delete
        
        old_backups = backups[keep:]
        deleted_count = 0
        
        for backup in old_backups:
            try:
                shutil.rmtree(backup.backup_path)
                logger.debug(f"Removed old backup: {backup.backup_id}")
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to remove old backup {backup.backup_id}: {e}")
        
        return deleted_count