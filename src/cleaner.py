import os
import shutil
import ctypes
import stat
from pathlib import Path
from typing import List, Tuple


class FileCleaner:
    def __init__(self):
        self.deleted_count = 0
        self.failed_count = 0
        self.errors = []
    
    def remove_readonly(self, func, path, excinfo):
        if os.path.exists(path):
            os.chmod(path, stat.S_IWRITE)
            func(path)
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        try:
            path = Path(file_path)
            if not path.exists():
                return False, f"文件不存在: {file_path}"
            
            if path.is_file():
                os.chmod(path, stat.S_IWRITE)
                os.remove(path)
            elif path.is_dir():
                shutil.rmtree(path, onerror=self.remove_readonly)
            
            self.deleted_count += 1
            return True, f"成功删除: {file_path}"
        except Exception as e:
            self.failed_count += 1
            error_msg = f"删除失败 [{file_path}]: {str(e)}"
            self.errors.append(error_msg)
            return False, error_msg
    
    def delete_batch(self, paths: List[str]) -> dict:
        results = {
            'success': [],
            'failed': [],
            'total': len(paths)
        }
        
        for path in paths:
            success, message = self.delete_file(path)
            if success:
                results['success'].append(path)
            else:
                results['failed'].append({'path': path, 'error': message})
        
        return results
    
    def get_file_info(self, path: str) -> dict:
        try:
            p = Path(path)
            if not p.exists():
                return {'exists': False, 'path': path}
            
            info = {
                'exists': True,
                'path': str(p.absolute()),
                'name': p.name,
                'is_dir': p.is_dir(),
                'size': 0
            }
            
            if p.is_file():
                info['size'] = p.stat().st_size
            elif p.is_dir():
                total_size = 0
                for item in p.rglob('*'):
                    if item.is_file():
                        total_size += item.stat().st_size
                info['size'] = total_size
            
            info['size_str'] = self._format_size(info['size'])
            return info
        except Exception as e:
            return {'exists': False, 'path': path, 'error': str(e)}
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def get_files_info(self, paths: List[str]) -> List[dict]:
        return [self.get_file_info(p) for p in paths]
