import winreg
import sys
import os
from pathlib import Path


class RegistryManager:
    REG_KEY_FILE = r"Software\Classes\*\shell\FileCleaner"
    REG_KEY_DIR = r"Software\Classes\Directory\shell\FileCleaner"
    REG_KEY_BACKGROUND = r"Software\Classes\Directory\Background\shell\FileCleaner"
    APP_NAME = "永久删除"
    
    def __init__(self):
        self.exe_path = self._get_exe_path()
    
    def _get_exe_path(self) -> str:
        if getattr(sys, 'frozen', False):
            return sys.executable
        return str(Path(__file__).parent.parent / "main.py")
    
    def add_context_menu(self) -> tuple:
        results = []
        try:
            self._add_menu_key(self.REG_KEY_FILE, "文件")
            results.append(("文件右键菜单", True, ""))
        except Exception as e:
            results.append(("文件右键菜单", False, str(e)))
        
        try:
            self._add_menu_key(self.REG_KEY_DIR, "文件夹")
            results.append(("文件夹右键菜单", True, ""))
        except Exception as e:
            results.append(("文件夹右键菜单", False, str(e)))
        
        return results
    
    def _add_menu_key(self, key_path: str, item_type: str):
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, self.APP_NAME)
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, "shell32.dll,-240")
        winreg.SetValueEx(key, "MultiSelectModel", 0, winreg.REG_SZ, "Player")
        winreg.CloseKey(key)
        
        command_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{key_path}\\command")
        command = f'"{self.exe_path}" "%1"'
        winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, command)
        winreg.CloseKey(command_key)
    
    def remove_context_menu(self) -> tuple:
        results = []
        for key_path, name in [
            (self.REG_KEY_FILE, "文件右键菜单"),
            (self.REG_KEY_DIR, "文件夹右键菜单")
        ]:
            try:
                self._remove_menu_key(key_path)
                results.append((name, True, ""))
            except Exception as e:
                results.append((name, False, str(e)))
        
        return results
    
    def _remove_menu_key(self, key_path: str):
        try:
            command_key = f"{key_path}\\command"
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, command_key)
        except WindowsError:
            pass
        
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
        except WindowsError:
            pass
    
    def is_context_menu_installed(self) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_KEY_FILE)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False
    
    def get_installation_status(self) -> dict:
        status = {
            'file_menu': False,
            'dir_menu': False,
            'exe_path': self.exe_path
        }
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_KEY_FILE)
            winreg.CloseKey(key)
            status['file_menu'] = True
        except WindowsError:
            pass
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_KEY_DIR)
            winreg.CloseKey(key)
            status['dir_menu'] = True
        except WindowsError:
            pass
        
        return status
