import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox
from src.cleaner import FileCleaner
from src.registry import RegistryManager
from src.gui import ConfirmDialog, ProgressDialog, ResultDialog
from src.utils import (
    parse_command_args, ensure_single_instance,
    get_instance_lock, write_paths_to_aggregation_file,
    read_and_clear_aggregation_file
)


class FileCleanerApp:
    def __init__(self, auto_mode=False):
        self.root = tk.Tk()
        self.root.title("文件清理工具")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        self.cleaner = FileCleaner()
        self.registry = RegistryManager()
        self.auto_mode = auto_mode
        
        self._setup_ui()
        self._check_command_args()
    
    def _setup_ui(self):
        self.root.configure(bg='#f5f5f5')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="🗑️ 文件清理工具",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="永久删除文件，绕过回收站",
            font=("Arial", 10),
            foreground="gray"
        )
        subtitle_label.pack()
        
        status_frame = ttk.LabelFrame(main_frame, text="右键菜单状态", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(
            status_frame,
            text="",
            font=("Arial", 10)
        )
        self.status_label.pack()
        
        self._update_status()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(
            button_frame,
            text="安装右键菜单",
            command=self._install_menu,
            width=20
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="卸载右键菜单",
            command=self._uninstall_menu,
            width=20
        ).pack(side=tk.LEFT)
        
        manual_frame = ttk.LabelFrame(main_frame, text="手动删除", padding="10")
        manual_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            manual_frame,
            text="输入要删除的文件/文件夹路径（每行一个）:",
            font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        self.path_text = tk.Text(manual_frame, height=8, width=50)
        self.path_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        ttk.Button(
            manual_frame,
            text="删除选中项目",
            command=self._manual_delete,
            width=20
        ).pack()
        
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(15, 0))
        
        info_label = ttk.Label(
            info_frame,
            text='提示：安装右键菜单后，可在文件/文件夹上右键选择"永久删除"',
            font=("Arial", 9),
            foreground="gray"
        )
        info_label.pack()
    
    def _update_status(self):
        status = self.registry.get_installation_status()
        
        if status['file_menu'] and status['dir_menu']:
            self.status_label.config(
                text='✅ 右键菜单已安装\n您可以在文件或文件夹上右键选择"永久删除"',
                foreground="green"
            )
        elif status['file_menu'] or status['dir_menu']:
            self.status_label.config(
                text="⚠️ 右键菜单部分安装",
                foreground="orange"
            )
        else:
            self.status_label.config(
                text="❌ 右键菜单未安装\n点击下方按钮安装右键菜单功能",
                foreground="red"
            )
    
    def _install_menu(self):
        results = self.registry.add_context_menu()
        
        success_all = all(r[1] for r in results)
        
        if success_all:
            messagebox.showinfo(
                "安装成功",
                '右键菜单安装成功！\n现在您可以在文件或文件夹上右键选择"永久删除"。'
            )
        else:
            messages = []
            for name, success, error in results:
                if success:
                    messages.append(f"✅ {name}: 成功")
                else:
                    messages.append(f"❌ {name}: 失败 - {error}")
            
            messagebox.showwarning(
                "安装结果",
                "\n".join(messages)
            )
        
        self._update_status()
    
    def _uninstall_menu(self):
        results = self.registry.remove_context_menu()
        
        success_all = all(r[1] for r in results)
        
        if success_all:
            messagebox.showinfo(
                "卸载成功",
                "右键菜单已卸载。"
            )
        else:
            messages = []
            for name, success, error in results:
                if success:
                    messages.append(f"✅ {name}: 成功")
                else:
                    messages.append(f"❌ {name}: 失败 - {error}")
            
            messagebox.showwarning(
                "卸载结果",
                "\n".join(messages)
            )
        
        self._update_status()
    
    def _manual_delete(self):
        text = self.path_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入要删除的文件路径")
            return
        
        paths = [p.strip() for p in text.split('\n') if p.strip()]
        valid_paths = [p for p in paths if os.path.exists(p)]
        
        if not valid_paths:
            messagebox.showwarning("提示", "没有找到有效的文件路径")
            return
        
        self._perform_delete(valid_paths)
    
    def _check_command_args(self):
        paths = parse_command_args()
        if not paths:
            return
        
        # 有命令行参数，进入自动模式
        self.auto_mode = True
        self.root.withdraw()
        
        lock = get_instance_lock()
        try:
            lock.acquire()
            # 获取到锁 = 主实例
            write_paths_to_aggregation_file(paths)
            # 等待其他进程写入路径
            time.sleep(0.6)
            # 读取所有聚合路径
            all_paths = read_and_clear_aggregation_file()
            if all_paths:
                self.root.after(100, lambda: self._perform_delete(all_paths))
            else:
                self.root.quit()
        except Exception:
            # 未获取到锁 = 非主实例，写入路径后退出
            write_paths_to_aggregation_file(paths)
            self.root.quit()
    
    def _perform_delete(self, paths):
        files_info = self.cleaner.get_files_info(paths)
        valid_files = [f for f in files_info if f.get('exists', False)]
        
        if not valid_files:
            messagebox.showwarning("提示", "没有有效的文件可删除")
            if self.auto_mode:
                self.root.quit()
            return
        
        confirm = ConfirmDialog(self.root, valid_files, None)
        if not confirm.show():
            if self.auto_mode:
                self.root.quit()
            return
        
        progress = ProgressDialog(self.root, "正在删除...")
        
        def delete_task():
            results = self.cleaner.delete_batch(paths)
            self.root.after(0, lambda: self._on_delete_complete(results, progress))
        
        import threading
        thread = threading.Thread(target=delete_task, daemon=True)
        thread.start()
    
    def _on_delete_complete(self, results, progress):
        progress.close()
        ResultDialog(self.root, results).show()
        if self.auto_mode:
            self.root.quit()
    
    def run(self):
        self._center_window()
        self.root.mainloop()
    
    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")


def main():
    app = FileCleanerApp()
    app.run()


if __name__ == "__main__":
    main()
