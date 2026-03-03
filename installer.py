import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.registry import RegistryManager
from src.utils import is_admin


def install():
    print("=" * 50)
    print("文件清理工具 - 右键菜单安装程序")
    print("=" * 50)
    
    registry = RegistryManager()
    
    print("\n正在安装右键菜单...")
    results = registry.add_context_menu()
    
    print("\n安装结果:")
    for name, success, error in results:
        if success:
            print(f"  ✅ {name}: 成功")
        else:
            print(f"  ❌ {name}: 失败 - {error}")
    
    if all(r[1] for r in results):
        print("\n✅ 安装成功！")
        print("现在您可以在文件或文件夹上右键选择"永久删除"。")
    else:
        print("\n⚠️ 部分安装失败，请检查错误信息。")


def uninstall():
    print("=" * 50)
    print("文件清理工具 - 右键菜单卸载程序")
    print("=" * 50)
    
    registry = RegistryManager()
    
    print("\n正在卸载右键菜单...")
    results = registry.remove_context_menu()
    
    print("\n卸载结果:")
    for name, success, error in results:
        if success:
            print(f"  ✅ {name}: 成功")
        else:
            print(f"  ❌ {name}: 失败 - {error}")
    
    if all(r[1] for r in results):
        print("\n✅ 卸载成功！")
    else:
        print("\n⚠️ 部分卸载失败，请检查错误信息。")


def show_status():
    print("=" * 50)
    print("文件清理工具 - 状态检查")
    print("=" * 50)
    
    registry = RegistryManager()
    status = registry.get_installation_status()
    
    print(f"\n程序路径: {status['exe_path']}")
    print(f"文件右键菜单: {'已安装 ✅' if status['file_menu'] else '未安装 ❌'}")
    print(f"文件夹右键菜单: {'已安装 ✅' if status['dir_menu'] else '未安装 ❌'}")


def main():
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python installer.py install   - 安装右键菜单")
        print("  python installer.py uninstall - 卸载右键菜单")
        print("  python installer.py status    - 查看状态")
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install()
    elif command == "uninstall":
        uninstall()
    elif command == "status":
        show_status()
    else:
        print(f"未知命令: {command}")
        print("可用命令: install, uninstall, status")
    
    print("\n按任意键退出...")
    input()


if __name__ == "__main__":
    main()
