from PIL import Image, ImageDraw, ImageFont
import os

class TextWatermark:
    """
    文本水印类，负责在图片上添加文本水印
    """
    
    def __init__(self):
        self.text = "水印文本"
        self.font_family = "arial.ttf"  # 默认字体
        self.font_size = 36
        self.color = (255, 255, 255)  # 白色
        self.opacity = 128  # 透明度 0-255
        self.position = (50, 50)  # 默认位置 (x, y)
        self.rotation = 0  # 旋转角度
    
    def set_text(self, text: str):
        """设置水印文本"""
        self.text = text
    
    def set_font(self, font_family: str, font_size: int):
        """设置字体"""
        self.font_family = font_family
        self.font_size = font_size
    
    def set_color(self, color: tuple):
        """设置文字颜色 (R, G, B)"""
        self.color = color
    
    def set_opacity(self, opacity: int):
        """设置透明度 (0-255)"""
        self.opacity = max(0, min(255, opacity))
    
    def set_position(self, position: tuple):
        """设置水印位置 (x, y)"""
        self.position = position
    
    def set_rotation(self, rotation: int):
        """设置旋转角度"""
        self.rotation = rotation
    
    def add_watermark(self, image: Image.Image) -> Image.Image:
        """
        在图片上添加文本水印
        
        Args:
            image: 原始图片
            
        Returns:
            添加水印后的图片
        """
        # 创建水印图层
        watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype(self.font_family, self.font_size)
        except:
            font = ImageFont.load_default()
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), self.text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 调整位置以确保文本在图片内
        x = max(0, min(self.position[0], image.width - text_width))
        y = max(0, min(self.position[1], image.height - text_height))
        
        # 绘制文本水印
        text_color = (*self.color, self.opacity)
        draw.text((x, y), self.text, font=font, fill=text_color)
        
        # 如果需要旋转，则旋转水印
        if self.rotation != 0:
            watermark_layer = watermark_layer.rotate(self.rotation, expand=0)
        
        # 将水印图层合并到原始图片
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        watermarked_image = Image.alpha_composite(image, watermark_layer)
        
        return watermarked_image
    
    def get_font_families(self):
        """
        获取系统可用字体列表
        注意：这是一个简化的实现，在实际应用中可能需要更复杂的字体检测机制
        """
        # 常见的系统字体
        common_fonts = [
            "arial.ttf",
            "simhei.ttf",  # 黑体
            "simsun.ttc",  # 宋体
            "msyh.ttc",    # 微软雅黑
            "calibri.ttf",
            "times.ttf"
        ]
        
        available_fonts = []
        for font in common_fonts:
            try:
                ImageFont.truetype(font, 12)
                available_fonts.append(font)
            except:
                continue
                
        return available_fonts if available_fonts else ["default"]