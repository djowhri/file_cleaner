import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable
import threading


class ConfirmDialog:
    def __init__(self, parent, files_info: List[dict], on_confirm: Callable):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("确认永久删除")
        self.dialog.geometry("600x400")
        self.dialog.resizable(True, True)
        self.files_info = files_info
        self.on_confirm = on_confirm
        self.result = False
        
        self._setup_ui()
        self._center_window()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 10))
        
        warning_icon = ttk.Label(warning_frame, text="⚠️", font=("Arial", 24))
        warning_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        warning_text = ttk.Label(
            warning_frame,
            text="警告：以下文件将被永久删除，无法恢复！\n此操作将绕过回收站，请谨慎操作。",
            font=("Arial", 10),
            foreground="red"
        )
        warning_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        list_frame = ttk.LabelFrame(main_frame, text="待删除文件列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = ("名称", "类型", "大小", "路径")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("名称", text="名称")
        self.tree.heading("类型", text="类型")
        self.tree.heading("大小", text="大小")
        self.tree.heading("路径", text="路径")
        
        self.tree.column("名称", width=150)
        self.tree.column("类型", width=80)
        self.tree.column("大小", width=100)
        self.tree.column("路径", width=250)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._populate_files()
        
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_size = sum(f.get('size', 0) for f in self.files_info)
        total_size_str = self._format_size(total_size)
        
        summary_label = ttk.Label(
            summary_frame,
            text=f"共 {len(self.files_info)} 个项目，总大小: {total_size_str}",
            font=("Arial", 10, "bold")
        )
        summary_label.pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="确认删除",
            command=self._on_confirm_click,
            width=15
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="取消",
            command=self._on_cancel_click,
            width=15
        ).pack(side=tk.RIGHT)
    
    def _populate_files(self):
        for info in self.files_info:
            if not info.get('exists', False):
                continue
            
            name = info.get('name', '')
            file_type = "文件夹" if info.get('is_dir', False) else "文件"
            size = info.get('size_str', '0 B')
            path = info.get('path', '')
            
            self.tree.insert("", tk.END, values=(name, file_type, size, path))
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def _on_confirm_click(self):
        self.result = True
        self.dialog.destroy()
    
    def _on_cancel_click(self):
        self.result = False
        self.dialog.destroy()
    
    def _center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def show(self) -> bool:
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.wait_window()
        return self.result


class ProgressDialog:
    def __init__(self, parent, title: str = "处理中"):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._setup_ui()
        self._center_window()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.label = ttk.Label(main_frame, text="正在删除文件...", font=("Arial", 10))
        self.label.pack(pady=(0, 10))
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=350)
        self.progress.pack(pady=(0, 10))
        self.progress.start(10)
        
        self.detail_label = ttk.Label(main_frame, text="", font=("Arial", 9))
        self.detail_label.pack()
    
    def update_status(self, text: str):
        self.label.config(text=text)
        self.dialog.update()
    
    def update_detail(self, text: str):
        self.detail_label.config(text=text)
        self.dialog.update()
    
    def _center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def close(self):
        self.progress.stop()
        self.dialog.destroy()


class ResultDialog:
    def __init__(self, parent, results: dict):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("删除结果")
        self.dialog.geometry("500x350")
        self.dialog.resizable(True, True)
        self.results = results
        
        self._setup_ui()
        self._center_window()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        success_count = len(self.results.get('success', []))
        failed_count = len(self.results.get('failed', []))
        total = self.results.get('total', 0)
        
        summary_frame = ttk.Frame(main_frame)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        if failed_count == 0:
            icon = "✅"
            color = "green"
        else:
            icon = "⚠️"
            color = "orange"
        
        icon_label = ttk.Label(summary_frame, text=icon, font=("Arial", 20))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        summary_text = f"删除完成！\n成功: {success_count} 个，失败: {failed_count} 个，总计: {total} 个"
        summary_label = ttk.Label(summary_frame, text=summary_text, font=("Arial", 10), foreground=color)
        summary_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        if failed_count > 0:
            failed_frame = ttk.LabelFrame(main_frame, text="失败项目", padding="5")
            failed_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            columns = ("路径", "错误信息")
            tree = ttk.Treeview(failed_frame, columns=columns, show="headings", height=8)
            
            tree.heading("路径", text="路径")
            tree.heading("错误信息", text="错误信息")
            
            tree.column("路径", width=250)
            tree.column("错误信息", width=200)
            
            scrollbar = ttk.Scrollbar(failed_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            for item in self.results.get('failed', []):
                tree.insert("", tk.END, values=(item.get('path', ''), item.get('error', '')))
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="确定",
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.RIGHT)
    
    def _center_window(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def show(self):
        self.dialog.transient()
        self.dialog.grab_set()
        self.dialog.wait_window()
