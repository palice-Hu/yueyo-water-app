<<<<<<< HEAD
# 水印工具 (Watermark Tool)

一个基于Python的桌面应用程序，用于给图片添加文本或图片水印。

## 功能特点

- 支持多种图片格式（JPEG, PNG, BMP, TIFF）
- 添加文本水印和图片水印
- 实时预览水印效果
- 自定义水印位置、透明度、字体等属性
- 批量处理图片
- 保存和加载水印模板

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python src/main.py
```

## 项目结构

```
watermark_app/
├── src/
│   ├── modules/     # 核心功能模块
│   ├── ui/          # 用户界面相关
│   └── utils/       # 工具类函数
├── tests/           # 测试文件
├── requirements.txt # 项目依赖
└── README.md        # 说明文档
```
=======
# 水印工具 (Watermark Tool)

一个基于Python的桌面应用程序，用于给图片添加文本或图片水印。

## 功能特点

- 支持多种图片格式（JPEG, PNG, BMP, TIFF）
- 添加文本水印和图片水印
- 实时预览水印效果
- 自定义水印位置、透明度、字体等属性
- 批量处理图片
- 保存和加载水印模板
- 支持九宫格预设位置和鼠标拖拽定位
- 支持文本水印的阴影和描边效果

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 开发环境运行
```bash
python src/main.py
```

### 打包为可执行文件
```bash
# 安装PyInstaller
pip install pyinstaller

# 方法1: 直接打包
pyinstaller --windowed --onefile src/main.py

# 方法2: 使用spec文件打包（推荐）
pyinstaller watermark_tool.spec
```

打包完成后，可执行文件将位于 `dist/` 目录中。

## 项目结构

```
watermark_app/
├── src/
│   ├── modules/     # 核心功能模块
│   ├── ui/          # 用户界面相关
│   └── utils/       # 工具类函数
├── tests/           # 测试文件
├── dist/            # 打包生成的可执行文件
├── build/           # PyInstaller构建目录
├── requirements.txt # 项目依赖
├── watermark_tool.spec # PyInstaller配置文件
└── README.md        # 说明文档
```
>>>>>>> main