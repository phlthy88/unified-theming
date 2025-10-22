"""
File utilities for Unified Theming Application.

This module provides utility functions for file operations with proper
error handling and fallback mechanisms.
"""
from pathlib import Path
from typing import Union, Optional
import chardet
from ..core.exceptions import FileReadError, FileWriteError, FilePermissionError

def read_file_with_fallback(file_path: Union[Path, str], encoding: Optional[str] = None) -> str:
    """
    Read a file with automatic encoding detection and fallback.
    
    Args:
        file_path: Path to file to read
        encoding: Preferred encoding (will attempt this first)
        
    Returns:
        File contents as string
        
    Raises:
        FileReadError: If file cannot be read
        FilePermissionError: If file access is denied
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileReadError(f"File does not exist: {path}")
    
    if not path.is_file():
        raise FileReadError(f"Path is not a file: {path}")
    
    # If no encoding specified, try common encodings in order of preference
    encodings_to_try = [encoding] if encoding else ["utf-8", "latin-1", "cp1252"]
    
    for enc in encodings_to_try:
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except PermissionError:
            raise FilePermissionError(path, "read")
        except OSError as e:
            raise FileReadError(f"Failed to read file {path}: {str(e)}", path=path)
    
    # If all encodings fail, try with chardet detection
    try:
        with open(path, 'rb') as f:
            raw_data = f.read()
        
        detected = chardet.detect(raw_data)
        detected_encoding = detected['encoding']
        
        if detected_encoding:
            try:
                return raw_data.decode(detected_encoding)
            except UnicodeDecodeError:
                pass
    except:
        pass
    
    # If all else fails, try reading with error handling
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except PermissionError:
        raise FilePermissionError(path, "read")
    except OSError as e:
        raise FileReadError(f"Failed to read file {path}: {str(e)}", path=path)


def write_file_with_backup(file_path: Union[Path, str], content: str, 
                          backup: bool = True) -> bool:
    """
    Write content to a file, optionally creating a backup of existing content.
    
    Args:
        file_path: Path to file to write
        content: Content to write
        backup: Whether to create a backup of existing file
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        FileWriteError: If file cannot be written
        FilePermissionError: If file access is denied
    """
    path = Path(file_path)
    
    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create backup if requested and file exists
    backup_path = None
    if backup and path.exists():
        backup_path = path.with_suffix(path.suffix + ".bak")
        try:
            backup_path.write_text(path.read_text())
        except Exception as e:
            raise FileWriteError(
                path, 
                f"Failed to create backup before writing: {str(e)}"
            )
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except PermissionError:
        if backup_path:
            # Restore from backup if write failed
            try:
                path.write_text(backup_path.read_text())
                backup_path.unlink()
            except:
                pass
        raise FilePermissionError(path, "write")
    except OSError as e:
        if backup_path:
            # Restore from backup if write failed
            try:
                path.write_text(backup_path.read_text())
                backup_path.unlink()
            except:
                pass
        raise FileWriteError(f"Failed to write file {path}: {str(e)}", path=path)


def ensure_directory_exists(dir_path: Union[Path, str]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        True if directory exists or was created successfully
    """
    path = Path(dir_path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        return False
    except OSError:
        return False


def safe_file_operation(file_path: Union[Path, str], operation, *args, **kwargs) -> bool:
    """
    Perform a file operation safely with proper error handling.
    
    Args:
        file_path: Path to file to operate on
        operation: Function to call on the file
        *args: Arguments to pass to the operation
        **kwargs: Keyword arguments to pass to the operation
        
    Returns:
        True if operation succeeded, False otherwise
    """
    try:
        result = operation(Path(file_path), *args, **kwargs)
        return result is not False
    except (FileReadError, FileWriteError, FilePermissionError):
        return False
    except Exception:
        return False