import io
import sys
import math
import logging
import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 单独提取字体加载逻辑，保持主函数干净
def load_custom_font():
    """尝试加载 Consolas 字体，如果失败则回退到默认"""
    font_name = "CustomConsolas"
    # 优先查找 Windows 常用路径
    font_filename = "consola.ttf" 
    possible_paths = [
        font_filename,
        os.path.join(r"C:\Windows\Fonts", font_filename),
        os.path.join(r"D:\Windows\Fonts", font_filename),
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts', font_filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
                return font_name
            except:
                continue
    return "Helvetica" # 回退字体

def add_page_numbers_simple(
    input_pdf_path: str,
    output_pdf_path: str,
    base_font_size: int = 12,
    min_font_size: int = 8,
    max_font_size: int = 48
):
    """
    为PDF的每一页添加与页面尺寸自适应的页码 (半透明纯文字版)。
    保持原有函数定义不变。
    """
    try:
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        
        # 加载字体
        font_name = load_custom_font()
        
        logger.info("开始为PDF添加页码（半透明纯文字模式），共 %d 页。", total_pages)

        # 遍历原始PDF的每一页
        for i, page in enumerate(reader.pages):
            page_num = i + 1
            
            # --- 1. 动态尺寸计算 ---
            # 必须使用 float 转换，否则某些 PDF 解析出来是 Decimal 对象会导致计算报错
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # 使用页面对角线长度作为衡量页面大小的指标
            page_diagonal = math.sqrt(page_width**2 + page_height**2)
            reference_diagonal = 1008.0 # A4 对角线参考
            
            scale_factor = page_diagonal / reference_diagonal
            
            # 稍微调小一点基准字体，纯文字不需要太大
            target_font_size = (base_font_size * 0.9) * scale_factor
            final_font_size = max(min_font_size, min(target_font_size, max_font_size))

            # 边距计算
            margin_right = 20.0 * scale_factor
            margin_bottom = 15.0 * scale_factor

            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=(page_width, page_height))

            # --- 2. 样式定义 ---
            text_content = f"{page_num} / {total_pages}"
            
            # 设置颜色：黑色，50% 透明度
            # 这种半透明效果类似水印，不刺眼，且能透出背景
            c.setFillColor(Color(0, 0, 0, alpha=0.5))
            
            # 设置字体
            c.setFont(font_name, final_font_size)
            
            # --- 3. 计算位置并绘制 ---
            # 获取文字宽度以实现右对齐
            text_width = c.stringWidth(text_content, font_name, final_font_size)
            
            x_pos = page_width - margin_right - text_width
            y_pos = margin_bottom
            
            c.drawString(x_pos, y_pos, text_content)
            
            # --- 4. 保存并合并 ---
            c.save()
            packet.seek(0)
            overlay_pdf = PdfReader(packet)
            page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)

        with open(output_pdf_path, "wb") as f:
            writer.write(f)
            
        logger.info("页码添加成功！已保存到文件：%s", output_pdf_path)

    except FileNotFoundError:
        logger.error("找不到输入文件 '%s'", input_pdf_path)
    except Exception as e:
        logger.error("处理过程中发生错误：%s", e)


# --- 使用示例 ---
if __name__ == "__main__":
    if len(sys.argv) != 3:
        # 你可以在这里修改默认值方便直接在编辑器里跑
        # input_file = "input.pdf"
        # output_file = "output.pdf"
        # add_page_numbers_simple(input_file, output_file)
        logger.error("使用方法: python your_script_name.py <input.pdf> <output.pdf>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        add_page_numbers_simple(input_file, output_file)