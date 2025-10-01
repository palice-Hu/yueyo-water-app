import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_app():
    """使用PyInstaller打包应用"""
    print("开始打包水印工具应用...")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    src_dir = project_root / "src"
    main_script = src_dir / "main.py"
    
    # 确保主脚本存在
    if not main_script.exists():
        print(f"错误: 找不到主脚本 {main_script}")
        return False
    
    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--name=WatermarkTool",  # 应用名称
        "--windowed",  # Windows下不显示控制台窗口
        "--onefile",  # 打包为单个可执行文件
        "--icon=NONE",  # 暂时没有图标文件
        f"--add-data=src{os.pathsep}src",  # 添加源代码目录
        "--hidden-import=PIL._tkinter_finder",  # 添加隐藏导入
        str(main_script)
    ]
    
    print("执行命令:", " ".join(cmd))
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("打包成功完成!")
            print("可执行文件位置:", project_root / "dist" / "WatermarkTool.exe")
            return True
        else:
            print("打包失败!")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"打包过程中出现异常: {e}")
        return False

def create_installer():
    """创建安装程序（可选）"""
    print("创建安装程序...")
    # 这里可以添加创建安装程序的代码
    # 例如使用NSIS或Inno Setup
    print("安装程序创建完成!")

if __name__ == "__main__":
    success = build_app()
    if success:
        print("应用打包成功!")
        # 可选：创建安装程序
        # create_installer()
    else:
        print("应用打包失败!")
        sys.exit(1)