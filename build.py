import PyInstaller.__main__
import sys
import os


def build():
    print("=" * 50)
    print("文件清理工具 - 打包脚本")
    print("=" * 50)
    
    main_script = os.path.join(os.path.dirname(__file__), "main.py")
    
    args = [
        main_script,
        '--name=FileCleaner',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        '--add-data=src;src',
        '--hidden-import=filelock',
    ]
    
    print("\n正在打包...")
    print(f"命令: pyinstaller {' '.join(args)}")
    
    PyInstaller.__main__.run(args)
    
    print("\n" + "=" * 50)
    print("✅ 打包完成！")
    print("可执行文件位于: dist/FileCleaner.exe")
    print("=" * 50)


if __name__ == "__main__":
    build()
