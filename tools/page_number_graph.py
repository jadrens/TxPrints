import io
import sys
import math
import logging
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white, gray, slategray

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_page_numbers_graph(
    input_pdf_path: str,
    output_pdf_path: str,
    base_font_size: int = 12,
    min_font_size: int = 8,
    max_font_size: int = 48
):
    """
    为PDF的每一页添加与页面尺寸自适应的、设计感强的页码。

    :param input_pdf_path: 输入的PDF文件路径。
    :param output_pdf_path: 添加页码后输出的PDF文件路径。
    :param base_font_size: 在标准页面（如A4）上的基础字体大小。
    :param min_font_size: 允许的最小字体大小。
    :param max_font_size: 允许的最大字体大小。
    """
    try:
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        
        logger.info("开始为PDF添加自适应尺寸的页码，共 %d 页。", total_pages)

        # 遍历原始PDF的每一页
        for i, page in enumerate(reader.pages):
            page_num = i + 1
            
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=page.mediabox.upper_right)

            # --- 1. 动态尺寸计算 ---
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # 使用页面对角线长度作为衡量页面大小的稳健指标
            page_diagonal = math.sqrt(page_width**2 + page_height**2)
            
            # 以 A4 纸的对角线长度 (约 1008.0) 作为参考基准
            # US Letter 的对角线约为 1000.0，两者相近
            reference_diagonal = 1008.0
            
            # 计算缩放因子
            scale_factor = page_diagonal / reference_diagonal
            
            # 根据缩放因子计算最终字体大小，并限制在最小和最大值之间
            target_font_size = base_font_size * scale_factor
            final_font_size = max(min_font_size, min(target_font_size, max_font_size))

            # 边距也应该根据页面大小进行缩放，并设置一个最小值
            base_margin = 35.0
            final_margin = max(15.0, base_margin * scale_factor)

            # --- 2. 智能样式与自动反色 ---
            is_odd_page = page_num % 2 != 0
            if is_odd_page: # 奇数页：深色主题
                bg_color, text_color, border_color = Color(0.2, 0.2, 0.2, alpha=0.9), white, slategray
            else: # 偶数页：浅色主题
                bg_color, text_color, border_color = Color(0.9, 0.9, 0.9, alpha=0.9), black, gray

            # 3. 定义样式和位置 (所有尺寸都使用动态计算的值)
            font_name = "Helvetica-Bold"
            page_text = f"{page_num}"
            
            radius = final_font_size * 1.1 
            
            x_center = page_width - final_margin - radius
            y_center = final_margin + radius
            
            # 4. 绘制图形
            c.setFillColor(bg_color)
            c.setStrokeColor(border_color)
            c.setLineWidth(1 * scale_factor) # 边框也缩放
            c.circle(x_center, y_center, radius, stroke=1, fill=1)
            
            c.setFillColor(text_color)
            c.setFont(font_name, final_font_size)
            c.drawCentredString(x_center, y_center - final_font_size * 0.35, page_text)
            
            # 5. 保存并合并
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
        logger.error("使用方法: python your_script_name.py <input.pdf> <output.pdf>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        add_page_numbers_graph(input_file, output_file)