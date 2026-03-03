# 🗑️ FileCleaner — 文件清理工具

一款 Windows 右键菜单集成的文件永久删除工具，绕过回收站直接删除，支持**批量框选**多个文件/文件夹一次性删除。

## ✨ 功能特性

- **右键菜单集成** — 在 Windows 资源管理器中右键即可使用"永久删除"
- **批量删除** — 框选多个文件/文件夹，只弹出一个确认框，一次性删除
- **安全确认** — 删除前展示详细的文件列表（名称、类型、大小、路径）
- **绕过回收站** — 文件直接永久删除，释放磁盘空间
- **进度反馈** — 删除过程中显示进度，完成后展示结果报告
- **手动模式** — 也可在主界面手动输入路径进行删除

## 📦 快速开始

### 方式一：使用打包好的 EXE（推荐）

1. 运行 `dist/FileCleaner.exe`
2. 点击 **"安装右键菜单"**
3. 在资源管理器中选中文件/文件夹 → 右键 → **"永久删除"**

### 方式二：从源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行主程序
python main.py
```

## 🔧 使用方式

### 右键菜单删除

1. 在资源管理器中选中一个或多个文件/文件夹
2. 右键点击 → 选择 **"永久删除"**
3. 在弹出的确认框中查看待删除文件列表
4. 点击 **"确认删除"** 执行删除，或点击 **"取消"** 放弃

### 手动删除

1. 打开 FileCleaner 主界面
2. 在文本框中输入文件/文件夹路径（每行一个）
3. 点击 **"删除选中项目"**

### 命令行安装/卸载右键菜单

```bash
python installer.py install    # 安装右键菜单
python installer.py uninstall  # 卸载右键菜单
python installer.py status     # 查看安装状态
```

## 🏗️ 项目结构

```
file_cleaner/
├── main.py              # 主程序入口
├── build.py             # PyInstaller 打包脚本
├── installer.py         # 右键菜单安装/卸载脚本（命令行）
├── requirements.txt     # 依赖列表
├── FileCleaner.spec     # PyInstaller 配置
├── src/
│   ├── gui.py           # GUI 组件（确认框、进度条、结果框）
│   ├── cleaner.py       # 文件删除核心逻辑
│   ├── registry.py      # Windows 注册表操作（右键菜单）
│   └── utils.py         # 工具函数（路径解析、实例聚合）
└── dist/
    └── FileCleaner.exe  # 打包后的可执行文件
```

## 🔨 自行打包

```bash
# 安装依赖
pip install -r requirements.txt

# 执行打包
python build.py
```

生成的 `FileCleaner.exe` 位于 `dist/` 目录下。

## ⚙️ 技术细节

### 多文件批量删除原理

当在资源管理器中框选多个文件右键删除时，Windows 会为每个文件启动一个独立进程。本工具通过 **单实例聚合** 机制解决多窗口问题：

1. 第一个进程获取文件锁，成为**主实例**
2. 后续进程将路径写入临时聚合文件后退出
3. 主实例等待 600ms 收集所有路径，然后统一弹出一个确认框

### 依赖

| 库 | 用途 |
|----|------|
| `tkinter` | GUI 界面（Python 内置） |
| `filelock` | 跨进程文件锁 |
| `pyinstaller` | 打包为 EXE |

## ⚠️ 注意事项

- 永久删除的文件**无法恢复**，请谨慎操作
- 安装/卸载右键菜单需要**当前用户权限**（写入 `HKEY_CURRENT_USER`）
- 仅支持 **Windows** 系统
