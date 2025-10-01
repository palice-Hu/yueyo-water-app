import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtWidgets import QFileDialog, QListWidget, QListWidgetItem, QGroupBox, QLineEdit, QSpinBox, QColorDialog
from PyQt5.QtWidgets import QComboBox, QSlider, QFormLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.file_handler import FileHandler
from modules.text_watermark import TextWatermark
from PIL import Image

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.text_watermark = TextWatermark()
        self.image_files = []  # 存储导入的图片文件路径
        self.current_image = None  # 当前选中的图片
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('水印工具')
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 - 图片列表和导入导出按钮
        left_panel = QVBoxLayout()
        
        # 图片导入区域
        import_group = QGroupBox("图片导入")
        import_layout = QVBoxLayout()
        self.import_btn = QPushButton("导入图片")
        self.import_btn.clicked.connect(self.import_images)
        self.import_folder_btn = QPushButton("导入文件夹")
        self.import_folder_btn.clicked.connect(self.import_folder)
        import_layout.addWidget(self.import_btn)
        import_layout.addWidget(self.import_folder_btn)
        import_group.setLayout(import_layout)
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.image_list.itemSelectionChanged.connect(self.on_image_selected)
        
        # 导出区域
        export_group = QGroupBox("导出设置")
        export_layout = QVBoxLayout()
        self.export_btn = QPushButton("导出图片")
        self.export_btn.clicked.connect(self.export_images)
        export_layout.addWidget(self.export_btn)
        export_group.setLayout(export_layout)
        
        left_panel.addWidget(import_group)
        left_panel.addWidget(self.image_list)
        left_panel.addWidget(export_group)
        
        # 右侧面板 - 水印设置
        right_panel = QVBoxLayout()
        
        # 文本水印设置区域
        text_watermark_group = QGroupBox("文本水印")
        text_layout = QFormLayout()
        
        # 文本内容
        self.text_input = QLineEdit("水印文本")
        self.text_input.textChanged.connect(lambda text: self.text_watermark.set_text(text))
        text_layout.addRow("文本内容:", self.text_input)
        
        # 字体大小
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(10, 100)
        self.font_size_input.setValue(36)
        self.font_size_input.valueChanged.connect(lambda size: self.text_watermark.set_font(self.text_watermark.font_family, size))
        text_layout.addRow("字体大小:", self.font_size_input)
        
        # 字体颜色
        color_layout = QHBoxLayout()
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.select_color)
        self.color_label = QLabel()
        self.color_label.setStyleSheet("background-color: rgb(255, 255, 255); border: 1px solid black;")
        self.color_label.setFixedWidth(50)
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_label)
        text_layout.addRow("字体颜色:", color_layout)
        
        # 透明度
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(128)
        self.opacity_slider.valueChanged.connect(lambda value: self.text_watermark.set_opacity(value))
        text_layout.addRow("透明度:", self.opacity_slider)
        
        text_watermark_group.setLayout(text_layout)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("请选择图片进行预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("border: 1px solid gray;")
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        
        right_panel.addWidget(text_watermark_group)
        right_panel.addWidget(preview_group)
        
        # 添加到主布局
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
    
    def import_images(self):
        """导入图片文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "选择图片文件", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_paths:
            # 筛选出支持的格式
            supported_files = self.file_handler.get_supported_files(file_paths)
            self.image_files.extend(supported_files)
            self.update_image_list()
    
    def import_folder(self):
        """导入整个文件夹的图片"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        
        if folder_path:
            try:
                image_files = self.file_handler.load_images_from_folder(folder_path)
                self.image_files.extend(image_files)
                self.update_image_list()
            except Exception as e:
                print(f"导入文件夹失败: {str(e)}")
    
    def update_image_list(self):
        """更新图片列表显示"""
        self.image_list.clear()
        for file_path in self.image_files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.UserRole, file_path)  # 保存完整路径
            self.image_list.addItem(item)
    
    def on_image_selected(self):
        """当图片被选中时"""
        selected_items = self.image_list.selectedItems()
        if selected_items:
            file_path = selected_items[0].data(Qt.UserRole)
            try:
                self.current_image = self.file_handler.load_image(file_path)
                self.update_preview()
            except Exception as e:
                print(f"加载图片失败: {str(e)}")
    
    def update_preview(self):
        """更新预览"""
        if self.current_image:
            # 添加水印
            watermarked_image = self.text_watermark.add_watermark(self.current_image.copy())
            # TODO: 显示预览图片
            self.preview_label.setText("预览功能将在下一阶段完善")
    
    def select_color(self):
        """选择字体颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())
            self.text_watermark.set_color(rgb)
            self.color_label.setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border: 1px solid black;")
    
    def export_images(self):
        """导出添加水印后的图片"""
        if not self.image_files:
            return
            
        # 选择导出目录
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not output_dir:
            return
            
        # 处理并导出每张图片
        for file_path in self.image_files:
            try:
                # 加载图片
                image = self.file_handler.load_image(file_path)
                
                # 添加水印
                watermarked_image = self.text_watermark.add_watermark(image)
                
                # 生成输出文件名
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                output_filename = f"{name}_watermarked{ext}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存图片
                self.file_handler.save_image(watermarked_image, output_path)
            except Exception as e:
                print(f"导出图片失败 {file_path}: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()