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