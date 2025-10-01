from PIL import Image, ImageDraw, ImageFont, ImageEnhance
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
        self.bold = False  # 粗体
        self.italic = False  # 斜体
        self.shadow = False  # 阴影效果
        self.shadow_color = (0, 0, 0)  # 阴影颜色
        self.shadow_offset = (2, 2)  # 阴影偏移
        self.stroke = False  # 描边效果
        self.stroke_color = (0, 0, 0)  # 描边颜色
        self.stroke_width = 1  # 描边宽度
    
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
    
    def set_bold(self, bold: bool):
        """设置粗体"""
        self.bold = bold
    
    def set_italic(self, italic: bool):
        """设置斜体"""
        self.italic = italic
    
    def set_shadow(self, shadow: bool, color: tuple = (0, 0, 0), offset: tuple = (2, 2)):
        """设置阴影效果"""
        self.shadow = shadow
        self.shadow_color = color
        self.shadow_offset = offset
    
    def set_stroke(self, stroke: bool, color: tuple = (0, 0, 0), width: int = 1):
        """设置描边效果"""
        self.stroke = stroke
        self.stroke_color = color
        self.stroke_width = width
    
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
        
        # 绘制阴影
        if self.shadow:
            shadow_x, shadow_y = x + self.shadow_offset[0], y + self.shadow_offset[1]
            shadow_color = (*self.shadow_color, int(self.opacity * 0.7))
            draw.text((shadow_x, shadow_y), self.text, font=font, fill=shadow_color)
        
        # 绘制描边
        if self.stroke:
            # 绘制多个偏移的文本来模拟描边效果
            for dx in range(-self.stroke_width, self.stroke_width + 1):
                for dy in range(-self.stroke_width, self.stroke_width + 1):
                    if dx != 0 or dy != 0:
                        stroke_x, stroke_y = x + dx, y + dy
                        stroke_color = (*self.stroke_color, int(self.opacity * 0.8))
                        draw.text((stroke_x, stroke_y), self.text, font=font, fill=stroke_color)
        
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