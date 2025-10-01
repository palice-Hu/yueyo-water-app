import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtWidgets import QFileDialog, QListWidget, QListWidgetItem, QGroupBox, QLineEdit, QSpinBox, QColorDialog
from PyQt5.QtWidgets import QComboBox, QSlider, QFormLayout, QCheckBox, QTabWidget, QRadioButton, QButtonGroup
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QGridLayout, QSizePolicy, QButtonGroup
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QImage, QColor

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.file_handler import FileHandler
from modules.text_watermark import TextWatermark
from modules.image_watermark import ImageWatermark
from modules.config_manager import ConfigManager
from utils.helpers import UIHelpers, ImageUtils
from PIL import Image

class DraggableLabel(QLabel):
    """
    可拖拽的标签，用于手动定位水印
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = None
        self.drag_start_position = QPoint()
        self.setMouseTracking(True)
        
    def set_parent_app(self, parent_app):
        self.parent_app = parent_app
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # 计算移动距离
            delta = event.pos() - self.drag_start_position
            
            # 更新水印位置
            if self.parent_app:
                if self.parent_app.watermark_type == "text":
                    current_pos = self.parent_app.text_watermark.position
                    new_pos = (current_pos[0] + delta.x(), current_pos[1] + delta.y())
                    self.parent_app.text_watermark.set_position(new_pos)
                else:
                    current_pos = self.parent_app.image_watermark.position
                    new_pos = (current_pos[0] + delta.x(), current_pos[1] + delta.y())
                    self.parent_app.image_watermark.set_position(new_pos)
                
                # 更新预览
                self.parent_app.update_preview()
                
            self.drag_start_position = event.pos()
    
    def mouseReleaseEvent(self, event):
        # 鼠标释放时更新位置输入框
        if self.parent_app:
            self.parent_app.update_position_inputs()

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.text_watermark = TextWatermark()
        self.image_watermark = ImageWatermark()
        self.config_manager = ConfigManager()
        self.image_files = []  # 存储导入的图片文件路径
        self.current_image = None  # 当前选中的图片
        self.current_watermark_image_path = None  # 当前水印图片路径
        self.watermark_type = "text"  # 水印类型：text 或 image
        self.initUI()
        self.load_last_config()
        
    def initUI(self):
        self.setWindowTitle('水印工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
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
        self.image_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
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
        
        # 中间面板 - 水印设置
        middle_panel = QVBoxLayout()
        
        # 水印类型选择
        type_group = QGroupBox("水印类型")
        type_layout = QHBoxLayout()
        self.text_radio = QRadioButton("文本水印")
        self.text_radio.setChecked(True)
        self.text_radio.toggled.connect(self.on_watermark_type_changed)
        self.image_radio = QRadioButton("图片水印")
        self.image_radio.toggled.connect(self.on_watermark_type_changed)
        type_layout.addWidget(self.text_radio)
        type_layout.addWidget(self.image_radio)
        type_layout.addStretch()
        type_group.setLayout(type_layout)
        
        # 水印设置标签页
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom-color: #cccccc;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: #e0e0e0;
                border-bottom-color: #e0e0e0;
            }
        """)
        
        # 文本水印设置
        self.create_text_watermark_tab()
        
        # 图片水印设置
        self.create_image_watermark_tab()
        
        # 模板管理标签页
        self.create_template_tab()
        
        middle_panel.addWidget(type_group)
        middle_panel.addWidget(self.settings_tabs)
        
        # 右侧面板 - 预览
        right_panel = QVBoxLayout()
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        self.preview_label = DraggableLabel("请选择图片进行预览")
        self.preview_label.set_parent_app(self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 500)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        
        right_panel.addWidget(preview_group)
        
        # 添加到主布局
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(middle_panel, 1)
        main_layout.addLayout(right_panel, 2)
    
    def create_text_watermark_tab(self):
        """创建文本水印设置标签页"""
        text_watermark_widget = QWidget()
        text_layout = QFormLayout()
        text_layout.setLabelAlignment(Qt.AlignRight)
        
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
        self.color_label.setStyleSheet("background-color: rgb(255, 255, 255); border: 1px solid black; border-radius: 4px;")
        self.color_label.setFixedWidth(50)
        self.color_label.setFixedHeight(25)
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_label)
        text_layout.addRow("字体颜色:", color_layout)
        
        # 透明度
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(128)
        self.opacity_slider.valueChanged.connect(lambda value: self.text_watermark.set_opacity(value))
        text_layout.addRow("透明度:", self.opacity_slider)
        
        # 位置坐标
        position_layout = QHBoxLayout()
        self.x_position_input = QSpinBox()
        self.x_position_input.setRange(0, 5000)
        self.x_position_input.setValue(50)
        self.x_position_input.valueChanged.connect(self.on_position_changed)
        self.y_position_input = QSpinBox()
        self.y_position_input.setRange(0, 5000)
        self.y_position_input.setValue(50)
        self.y_position_input.valueChanged.connect(self.on_position_changed)
        position_layout.addWidget(QLabel("X:"))
        position_layout.addWidget(self.x_position_input)
        position_layout.addWidget(QLabel("Y:"))
        position_layout.addWidget(self.y_position_input)
        text_layout.addRow("位置坐标:", position_layout)
        
        # 九宫格预设位置
        preset_layout = QGridLayout()
        positions = [
            ("左上", "top-left"), ("上中", "top-center"), ("右上", "top-right"),
            ("左中", "center-left"), ("居中", "center"), ("右中", "center-right"),
            ("左下", "bottom-left"), ("下中", "bottom-center"), ("右下", "bottom-right")
        ]
        
        self.position_buttons = {}
        for i, (label, pos) in enumerate(positions):
            row = i // 3
            col = i % 3
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, p=pos: self.set_preset_position(p))
            preset_layout.addWidget(btn, row, col)
            self.position_buttons[pos] = btn
        
        position_group = QGroupBox("预设位置")
        position_group.setLayout(preset_layout)
        text_layout.addRow(position_group)
        
        # 旋转角度
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(0, 360)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(lambda value: self.text_watermark.set_rotation(value))
        self.rotation_label = QLabel("0°")
        self.rotation_label.setFixedWidth(30)
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(self.rotation_slider)
        rotation_layout.addWidget(self.rotation_label)
        text_layout.addRow("旋转角度:", rotation_layout)
        
        # 高级文本设置
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QVBoxLayout()
        
        # 粗体和斜体
        style_layout = QHBoxLayout()
        self.bold_checkbox = QCheckBox("粗体")
        self.bold_checkbox.stateChanged.connect(lambda state: self.text_watermark.set_bold(state == Qt.Checked))
        self.italic_checkbox = QCheckBox("斜体")
        self.italic_checkbox.stateChanged.connect(lambda state: self.text_watermark.set_italic(state == Qt.Checked))
        style_layout.addWidget(self.bold_checkbox)
        style_layout.addWidget(self.italic_checkbox)
        advanced_layout.addLayout(style_layout)
        
        # 阴影效果
        shadow_layout = QHBoxLayout()
        self.shadow_checkbox = QCheckBox("阴影效果")
        self.shadow_checkbox.stateChanged.connect(self.on_shadow_changed)
        shadow_layout.addWidget(self.shadow_checkbox)
        advanced_layout.addLayout(shadow_layout)
        
        # 描边效果
        stroke_layout = QHBoxLayout()
        self.stroke_checkbox = QCheckBox("描边效果")
        self.stroke_checkbox.stateChanged.connect(self.on_stroke_changed)
        stroke_layout.addWidget(self.stroke_checkbox)
        advanced_layout.addLayout(stroke_layout)
        
        advanced_group.setLayout(advanced_layout)
        text_layout.addRow(advanced_group)
        
        text_watermark_widget.setLayout(text_layout)
        self.settings_tabs.addTab(text_watermark_widget, "文本水印")
    
    def create_image_watermark_tab(self):
        """创建图片水印设置标签页"""
        image_watermark_widget = QWidget()
        image_layout = QFormLayout()
        image_layout.setLabelAlignment(Qt.AlignRight)
        
        # 图片水印导入
        import_layout = QHBoxLayout()
        self.import_watermark_btn = QPushButton("导入水印图片")
        self.import_watermark_btn.clicked.connect(self.import_watermark_image)
        self.watermark_preview = QLabel("无水印图片")
        self.watermark_preview.setFixedHeight(100)
        self.watermark_preview.setAlignment(Qt.AlignCenter)
        self.watermark_preview.setStyleSheet("border: 1px solid gray; border-radius: 4px;")
        import_layout.addWidget(self.import_watermark_btn)
        import_layout.addWidget(self.watermark_preview)
        image_layout.addRow("水印图片:", import_layout)
        
        # 位置坐标
        position_layout = QHBoxLayout()
        self.image_x_position_input = QSpinBox()
        self.image_x_position_input.setRange(0, 5000)
        self.image_x_position_input.setValue(0)
        self.image_x_position_input.valueChanged.connect(self.on_image_position_changed)
        self.image_y_position_input = QSpinBox()
        self.image_y_position_input.setRange(0, 5000)
        self.image_y_position_input.setValue(0)
        self.image_y_position_input.valueChanged.connect(self.on_image_position_changed)
        position_layout.addWidget(QLabel("X:"))
        position_layout.addWidget(self.image_x_position_input)
        position_layout.addWidget(QLabel("Y:"))
        position_layout.addWidget(self.image_y_position_input)
        image_layout.addRow("位置坐标:", position_layout)
        
        # 九宫格预设位置
        preset_layout = QGridLayout()
        positions = [
            ("左上", "top-left"), ("上中", "top-center"), ("右上", "top-right"),
            ("左中", "center-left"), ("居中", "center"), ("右中", "center-right"),
            ("左下", "bottom-left"), ("下中", "bottom-center"), ("右下", "bottom-right")
        ]
        
        self.image_position_buttons = {}
        for i, (label, pos) in enumerate(positions):
            row = i // 3
            col = i % 3
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, p=pos: self.set_image_preset_position(p))
            preset_layout.addWidget(btn, row, col)
            self.image_position_buttons[pos] = btn
        
        position_group = QGroupBox("预设位置")
        position_group.setLayout(preset_layout)
        image_layout.addRow(position_group)
        
        # 缩放
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(1, 200)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(lambda value: self.image_watermark.set_scale(value / 100.0))
        image_layout.addRow("缩放比例:", self.scale_slider)
        
        # 透明度
        self.image_opacity_slider = QSlider(Qt.Horizontal)
        self.image_opacity_slider.setRange(0, 255)
        self.image_opacity_slider.setValue(128)
        self.image_opacity_slider.valueChanged.connect(lambda value: self.image_watermark.set_opacity(value))
        image_layout.addRow("透明度:", self.image_opacity_slider)
        
        # 旋转角度
        self.image_rotation_slider = QSlider(Qt.Horizontal)
        self.image_rotation_slider.setRange(0, 360)
        self.image_rotation_slider.setValue(0)
        self.image_rotation_slider.valueChanged.connect(lambda value: self.image_watermark.set_rotation(value))
        self.image_rotation_label = QLabel("0°")
        self.image_rotation_label.setFixedWidth(30)
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(self.image_rotation_slider)
        rotation_layout.addWidget(self.image_rotation_label)
        image_layout.addRow("旋转角度:", rotation_layout)
        
        image_watermark_widget.setLayout(image_layout)
        self.settings_tabs.addTab(image_watermark_widget, "图片水印")
    
    def create_template_tab(self):
        """创建模板管理标签页"""
        template_widget = QWidget()
        template_layout = QVBoxLayout()
        
        # 文本水印模板
        text_template_group = QGroupBox("文本水印模板")
        text_template_layout = QVBoxLayout()
        
        # 模板列表
        self.text_template_list = QListWidget()
        self.text_template_list.itemClicked.connect(self.load_text_template)
        text_template_layout.addWidget(self.text_template_list)
        
        # 模板操作按钮
        text_template_btn_layout = QHBoxLayout()
        self.save_text_template_btn = QPushButton("保存模板")
        self.save_text_template_btn.clicked.connect(self.save_text_template)
        self.delete_text_template_btn = QPushButton("删除模板")
        self.delete_text_template_btn.clicked.connect(self.delete_text_template)
        text_template_btn_layout.addWidget(self.save_text_template_btn)
        text_template_btn_layout.addWidget(self.delete_text_template_btn)
        text_template_layout.addLayout(text_template_btn_layout)
        
        text_template_group.setLayout(text_template_layout)
        
        # 图片水印模板
        image_template_group = QGroupBox("图片水印模板")
        image_template_layout = QVBoxLayout()
        
        # 模板列表
        self.image_template_list = QListWidget()
        self.image_template_list.itemClicked.connect(self.load_image_template)
        image_template_layout.addWidget(self.image_template_list)
        
        # 模板操作按钮
        image_template_btn_layout = QHBoxLayout()
        self.save_image_template_btn = QPushButton("保存模板")
        self.save_image_template_btn.clicked.connect(self.save_image_template)
        self.delete_image_template_btn = QPushButton("删除模板")
        self.delete_image_template_btn.clicked.connect(self.delete_image_template)
        image_template_btn_layout.addWidget(self.save_image_template_btn)
        image_template_btn_layout.addWidget(self.delete_image_template_btn)
        image_template_layout.addLayout(image_template_btn_layout)
        
        image_template_group.setLayout(image_template_layout)
        
        template_layout.addWidget(text_template_group)
        template_layout.addWidget(image_template_group)
        
        template_widget.setLayout(template_layout)
        self.settings_tabs.addTab(template_widget, "模板管理")
        
        # 加载模板列表
        self.refresh_template_lists()
    
    def refresh_template_lists(self):
        """刷新模板列表"""
        # 清空列表
        self.text_template_list.clear()
        self.image_template_list.clear()
        
        # 加载文本模板
        text_templates = self.config_manager.get_text_templates()
        for name in text_templates.keys():
            self.text_template_list.addItem(name)
        
        # 加载图片模板
        image_templates = self.config_manager.get_image_templates()
        for name in image_templates.keys():
            self.image_template_list.addItem(name)
    
    def save_text_template(self):
        """保存文本水印模板"""
        name, ok = QInputDialog.getText(self, "保存文本模板", "请输入模板名称:")
        if ok and name:
            # 获取当前文本水印设置
            settings = {
                "text": self.text_watermark.text,
                "font_family": self.text_watermark.font_family,
                "font_size": self.text_watermark.font_size,
                "color": self.text_watermark.color,
                "opacity": self.text_watermark.opacity,
                "position": self.text_watermark.position,
                "rotation": self.text_watermark.rotation,
                "bold": self.text_watermark.bold,
                "italic": self.text_watermark.italic,
                "shadow": self.text_watermark.shadow,
                "shadow_color": self.text_watermark.shadow_color,
                "shadow_offset": self.text_watermark.shadow_offset,
                "stroke": self.text_watermark.stroke,
                "stroke_color": self.text_watermark.stroke_color,
                "stroke_width": self.text_watermark.stroke_width
            }
            
            if self.config_manager.save_text_watermark_template(name, settings):
                QMessageBox.information(self, "成功", f"文本水印模板 '{name}' 保存成功!")
                self.refresh_template_lists()
            else:
                QMessageBox.warning(self, "错误", f"保存文本水印模板 '{name}' 失败!")
    
    def save_image_template(self):
        """保存图片水印模板"""
        name, ok = QInputDialog.getText(self, "保存图片模板", "请输入模板名称:")
        if ok and name:
            # 获取当前图片水印设置
            settings = {
                "position": self.image_watermark.position,
                "opacity": self.image_watermark.opacity,
                "scale": self.image_watermark.scale,
                "rotation": self.image_watermark.rotation
            }
            
            if self.config_manager.save_image_watermark_template(name, settings):
                QMessageBox.information(self, "成功", f"图片水印模板 '{name}' 保存成功!")
                self.refresh_template_lists()
            else:
                QMessageBox.warning(self, "错误", f"保存图片水印模板 '{name}' 失败!")
    
    def load_text_template(self, item):
        """加载文本水印模板"""
        name = item.text()
        settings = self.config_manager.load_text_watermark_template(name)
        
        if settings:
            # 应用模板设置
            self.text_watermark.set_text(settings.get("text", "水印文本"))
            self.text_watermark.set_font(
                settings.get("font_family", "arial.ttf"),
                settings.get("font_size", 36)
            )
            self.text_watermark.set_color(settings.get("color", (255, 255, 255)))
            self.text_watermark.set_opacity(settings.get("opacity", 128))
            self.text_watermark.set_position(settings.get("position", (50, 50)))
            self.text_watermark.set_rotation(settings.get("rotation", 0))
            self.text_watermark.set_bold(settings.get("bold", False))
            self.text_watermark.set_italic(settings.get("italic", False))
            self.text_watermark.set_shadow(
                settings.get("shadow", False),
                settings.get("shadow_color", (0, 0, 0)),
                settings.get("shadow_offset", (2, 2))
            )
            self.text_watermark.set_stroke(
                settings.get("stroke", False),
                settings.get("stroke_color", (0, 0, 0)),
                settings.get("stroke_width", 1)
            )
            
            # 更新UI控件
            self.text_input.setText(settings.get("text", "水印文本"))
            self.font_size_input.setValue(settings.get("font_size", 36))
            self.opacity_slider.setValue(settings.get("opacity", 128))
            self.bold_checkbox.setChecked(settings.get("bold", False))
            self.italic_checkbox.setChecked(settings.get("italic", False))
            self.shadow_checkbox.setChecked(settings.get("shadow", False))
            self.stroke_checkbox.setChecked(settings.get("stroke", False))
            self.rotation_slider.setValue(settings.get("rotation", 0))
            self.rotation_label.setText(f"{settings.get('rotation', 0)}°")
            
            position = settings.get("position", (50, 50))
            self.x_position_input.setValue(position[0])
            self.y_position_input.setValue(position[1])
            
            color = settings.get("color", (255, 255, 255))
            self.color_label.setStyleSheet(f"background-color: rgb({color[0]}, {color[1]}, {color[2]}); border: 1px solid black; border-radius: 4px;")
            
            QMessageBox.information(self, "成功", f"文本水印模板 '{name}' 加载成功!")
            self.update_preview()
        else:
            QMessageBox.warning(self, "错误", f"加载文本水印模板 '{name}' 失败!")
    
    def load_image_template(self, item):
        """加载图片水印模板"""
        name = item.text()
        settings = self.config_manager.load_image_watermark_template(name)
        
        if settings:
            # 应用模板设置
            self.image_watermark.set_position(settings.get("position", (0, 0)))
            self.image_watermark.set_opacity(settings.get("opacity", 128))
            self.image_watermark.set_scale(settings.get("scale", 1.0))
            self.image_watermark.set_rotation(settings.get("rotation", 0))
            
            # 更新UI控件
            self.image_opacity_slider.setValue(settings.get("opacity", 128))
            self.scale_slider.setValue(int(settings.get("scale", 1.0) * 100))
            self.image_rotation_slider.setValue(settings.get("rotation", 0))
            self.image_rotation_label.setText(f"{settings.get('rotation', 0)}°")
            
            position = settings.get("position", (0, 0))
            self.image_x_position_input.setValue(position[0])
            self.image_y_position_input.setValue(position[1])
            
            QMessageBox.information(self, "成功", f"图片水印模板 '{name}' 加载成功!")
            self.update_preview()
        else:
            QMessageBox.warning(self, "错误", f"加载图片水印模板 '{name}' 失败!")
    
    def delete_text_template(self):
        """删除选中的文本水印模板"""
        current_item = self.text_template_list.currentItem()
        if current_item:
            name = current_item.text()
            reply = QMessageBox.question(self, "确认删除", f"确定要删除文本水印模板 '{name}' 吗？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.config_manager.delete_text_template(name):
                    QMessageBox.information(self, "成功", f"文本水印模板 '{name}' 删除成功!")
                    self.refresh_template_lists()
                else:
                    QMessageBox.warning(self, "错误", f"删除文本水印模板 '{name}' 失败!")
        else:
            QMessageBox.warning(self, "警告", "请先选择要删除的文本模板!")
    
    def delete_image_template(self):
        """删除选中的图片水印模板"""
        current_item = self.image_template_list.currentItem()
        if current_item:
            name = current_item.text()
            reply = QMessageBox.question(self, "确认删除", f"确定要删除图片水印模板 '{name}' 吗？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.config_manager.delete_image_template(name):
                    QMessageBox.information(self, "成功", f"图片水印模板 '{name}' 删除成功!")
                    self.refresh_template_lists()
                else:
                    QMessageBox.warning(self, "错误", f"删除图片水印模板 '{name}' 失败!")
        else:
            QMessageBox.warning(self, "警告", "请先选择要删除的图片模板!")
    
    def on_watermark_type_changed(self):
        """当水印类型改变时"""
        if self.text_radio.isChecked():
            self.watermark_type = "text"
        else:
            self.watermark_type = "image"
        self.update_preview()
    
    def on_shadow_changed(self, state):
        """当阴影效果改变时"""
        if state == Qt.Checked:
            self.text_watermark.set_shadow(True)
        else:
            self.text_watermark.set_shadow(False)
        self.update_preview()
    
    def on_stroke_changed(self, state):
        """当描边效果改变时"""
        if state == Qt.Checked:
            self.text_watermark.set_stroke(True)
        else:
            self.text_watermark.set_stroke(False)
        self.update_preview()
    
    def on_position_changed(self):
        """当文本水印位置改变时"""
        x = self.x_position_input.value()
        y = self.y_position_input.value()
        self.text_watermark.set_position((x, y))
        self.update_preview()
    
    def on_image_position_changed(self):
        """当图片水印位置改变时"""
        x = self.image_x_position_input.value()
        y = self.image_y_position_input.value()
        self.image_watermark.set_position((x, y))
        self.update_preview()
    
    def set_preset_position(self, position_type):
        """设置文本水印预设位置"""
        if self.current_image:
            # 获取水印大小（简化处理）
            if self.watermark_type == "text":
                watermark_size = (100, 50)  # 简化处理，实际应该计算文本大小
                image_size = self.current_image.size
                position = ImageUtils.calculate_watermark_position(image_size, watermark_size, position_type)
                self.text_watermark.set_position(position)
                self.x_position_input.setValue(position[0])
                self.y_position_input.setValue(position[1])
                self.update_preview()
    
    def set_image_preset_position(self, position_type):
        """设置图片水印预设位置"""
        if self.current_image and self.image_watermark.watermark_image:
            watermark_size = self.image_watermark.watermark_image.size
            image_size = self.current_image.size
            position = ImageUtils.calculate_watermark_position(image_size, watermark_size, position_type)
            self.image_watermark.set_position(position)
            self.image_x_position_input.setValue(position[0])
            self.image_y_position_input.setValue(position[1])
            self.update_preview()
    
    def update_position_inputs(self):
        """更新位置输入框的值"""
        if self.watermark_type == "text":
            position = self.text_watermark.position
            self.x_position_input.setValue(position[0])
            self.y_position_input.setValue(position[1])
        else:
            position = self.image_watermark.position
            self.image_x_position_input.setValue(position[0])
            self.image_y_position_input.setValue(position[1])
    
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
                QMessageBox.warning(self, "错误", f"导入文件夹失败: {str(e)}")
    
    def import_watermark_image(self):
        """导入水印图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择水印图片",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            try:
                self.image_watermark.load_watermark(file_path)
                self.current_watermark_image_path = file_path
                
                # 显示水印图片预览
                pixmap = QPixmap(file_path)
                self.watermark_preview.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.watermark_preview.setText("")
                
                self.update_preview()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导入水印图片失败: {str(e)}")
    
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
                QMessageBox.warning(self, "错误", f"加载图片失败: {str(e)}")
    
    def update_preview(self):
        """更新预览"""
        if self.current_image:
            # 根据水印类型添加水印
            if self.watermark_type == "text":
                watermarked_image = self.text_watermark.add_watermark(self.current_image.copy())
            else:
                if self.image_watermark.watermark_image is None:
                    self.preview_label.setText("请先选择水印图片")
                    return
                watermarked_image = self.image_watermark.add_watermark(self.current_image.copy())
            
            # 显示预览图片
            self.display_image(watermarked_image)
    
    def display_image(self, image):
        """在预览区域显示图片"""
        try:
            # 转换PIL图像为QPixmap并显示
            pixmap = UIHelpers.create_pixmap_from_pil_image(image)
            
            # 缩放图片以适应预览区域
            scaled_pixmap = pixmap.scaled(
                self.preview_label.width() - 20, 
                self.preview_label.height() - 20, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.setText("")
        except Exception as e:
            self.preview_label.setText(f"预览错误: {str(e)}")
    
    def select_color(self):
        """选择字体颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())
            self.text_watermark.set_color(rgb)
            self.color_label.setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border: 1px solid black; border-radius: 4px;")
            self.update_preview()
    
    def export_images(self):
        """导出添加水印后的图片"""
        if not self.image_files:
            QMessageBox.warning(self, "警告", "请先导入图片!")
            return
            
        # 选择导出目录
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not output_dir:
            return
        
        success_count = 0
        fail_count = 0
            
        # 处理并导出每张图片
        for file_path in self.image_files:
            try:
                # 加载图片
                image = self.file_handler.load_image(file_path)
                
                # 添加水印
                if self.watermark_type == "text":
                    watermarked_image = self.text_watermark.add_watermark(image)
                else:
                    if self.image_watermark.watermark_image is not None:
                        watermarked_image = self.image_watermark.add_watermark(image)
                    else:
                        watermarked_image = image  # 没有水印图片时导出原图
                
                # 生成输出文件名
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                output_filename = f"{name}_watermarked{ext}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存图片
                self.file_handler.save_image(watermarked_image, output_path)
                success_count += 1
            except Exception as e:
                print(f"导出图片失败 {file_path}: {str(e)}")
                fail_count += 1
        
        # 显示导出结果
        QMessageBox.information(self, "导出完成", f"成功导出 {success_count} 张图片\n失败 {fail_count} 张图片")
    
    def load_last_config(self):
        """加载上次使用的配置"""
        try:
            config = self.config_manager.load_config()
            last_used = config.get("last_used", {})
            
            # 设置上次使用的水印类型
            watermark_type = last_used.get("watermark_type", "text")
            if watermark_type == "image":
                self.image_radio.setChecked(True)
                self.watermark_type = "image"
            else:
                self.text_radio.setChecked(True)
                self.watermark_type = "text"
        except Exception as e:
            print(f"加载上次配置失败: {str(e)}")
    
    def save_current_config(self):
        """保存当前配置"""
        try:
            config = self.config_manager.load_config()
            config["last_used"] = {
                "watermark_type": self.watermark_type
            }
            self.config_manager.save_config(config)
        except Exception as e:
            print(f"保存当前配置失败: {str(e)}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.save_current_config()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()