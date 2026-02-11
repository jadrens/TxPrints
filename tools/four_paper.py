import sys
import logging
from pypdf import PdfReader, PdfWriter, Transformation, PageObject
from decimal import Decimal

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def merge_pdf_pages_4_in_1_refactored(input_pdf_path, output_pdf_path):
    """
    将一个PDF文件的每4页合并到一页上。（重构版）

    采用“隔离-组合”策略来彻底解决页面重叠的Bug：
    1.  隔离：为每个待合并的页面创建一个临时的、干净的画布，并在上面执行单次的变换合并。
    2.  组合：将这些准备好的、各自独立的临时页面，再全部合并到最终的页面上。
    """
    try:
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()
        num_pages = len(reader.pages)

        if num_pages == 0:
            logger.warning("输入的PDF文件是空的。")
            return
        
        logger.info("开始处理，共找到 %d 页。", num_pages)

        for i in range(0, num_pages, 4):
            pages_in_group = [reader.pages[k] for k in range(i, min(i + 4, num_pages))]
            if not pages_in_group:
                continue

            # 步骤 1: 像以前一样，计算一个能容纳所有页面的最大画布尺寸
            max_width = Decimal(0)
            max_height = Decimal(0)
            for page in pages_in_group:
                if page.mediabox.width > max_width:
                    max_width = page.mediabox.width
                if page.mediabox.height > max_height:
                    max_height = page.mediabox.height
            
            if max_width == 0 or max_height == 0:
                logger.warning("从第 %d 页开始的组尺寸无效，跳过。", i+1)
                continue

            # 步骤 2: 创建最终要写入的空白页
            final_page = writer.add_blank_page(width=max_width, height=max_height)
            logger.info("为第 %d-%d 页创建最终画布，尺寸: %.1fx%.1f", i+1, min(i+4, num_pages), float(max_width), float(max_height))

            # 步骤 3: 遍历组内的每一页，执行“隔离-组合”
            target_width = max_width / 2
            target_height = max_height / 2
            target_positions = [
                (0, target_height),              # 左上
                (target_width, target_height),   # 右上
                (0, 0),                          # 左下
                (target_width, 0),               # 右下
            ]

            for j, source_page in enumerate(pages_in_group):
                page_index = i + j
                
                # --- 核心重构逻辑 ---
                
                # 3a. ISOLATE: 创建一个临时的、干净的、与最终画布等大的页面
                # 这是关键，确保每次变换合并操作都在一个全新的环境中进行
                temp_page = PageObject.create_blank_page(width=max_width, height=max_height)
                
                # 3b. 计算变换参数（这部分逻辑不变，因为是正确的）
                mb = source_page.mediabox
                op = Transformation().translate(tx=-mb.left, ty=-mb.bottom) # 先移到原点
                
                scale = min(target_width / mb.width, target_height / mb.height)
                op = op.scale(sx=scale, sy=scale)
                
                scaled_width = mb.width * scale
                scaled_height = mb.height * scale
                tx_target, ty_target = target_positions[j]
                final_tx = tx_target + (target_width - scaled_width) / 2
                final_ty = ty_target + (target_height - scaled_height) / 2
                op = op.translate(tx=final_tx, ty=final_ty)
                
                # 3c. 在这个临时的、干净的页面上执行【单次】变换合并
                temp_page.merge_transformed_page(source_page, op)

                # 3d. COMBINE: 将准备好的临时页面，通过简单的覆盖方式合并到最终页上
                # 因为 temp_page 除了一个象限有内容外，其他地方都是透明的，所以可以直接覆盖
                final_page.merge_page(temp_page)
                
                logger.info("  已隔离处理并组合第 %d 页到象限 %d", page_index + 1, j+1)

        with open(output_pdf_path, "wb") as f:
            writer.write(f)
            
        logger.info("成功将 %d 页合并到新的PDF文件：%s", num_pages, output_pdf_path)

    except FileNotFoundError:
        logger.error("找不到输入文件 '%s'", input_pdf_path)
    except Exception as e:
        logger.error("处理过程中发生严重错误：%s", e, exc_info=True)

merge_pdf_pages_4_in_1_compatible = merge_pdf_pages_4_in_1_refactored

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.error("使用方法: python your_script_name.py <input.pdf> <output.pdf>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        merge_pdf_pages_4_in_1_refactored(input_file, output_file)