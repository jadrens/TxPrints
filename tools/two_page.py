import os
import logging
import concurrent.futures
from io import BytesIO


from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_pdf_pages(pdf_path):
    """
    获取PDF文件的页数

    :param pdf_path: PDF文件路径
    :return: PDF页数
    """
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        return len(reader.pages)
    return None


INIT_PAGE = 4
PAGES = 8


def generate_print_page_numbers(init_page, pages, page_per_square=2, mode="first"):
    """
    由于打印机不支持正反打印，所以需要将页码分成两部分，然后分别打印

    :param init_page: 起始页码
    :param pages: 页面数量
    :param page_per_square: 每方格页数
    :param mode: 打印模式 ("first" 或其他)
    :return: 页码列表
    """
    offset = 0 if mode == "first" else 1
    seperation = page_per_square
    numbers = []
    for i in range(init_page, init_page+pages*seperation, seperation):
        numbers.append(i+offset)
        numbers.append(i+1+offset)
    return numbers


FOLD_PAGE_PER_SQUARE = 2


def generate_fold_pages(start_page, pages_log, reverse=False, last_skip=False):
    """
    生成折叠页码列表

    :param start_page: 起始页码（1-based）
    :param pages_log: 要处理的页数 one side of physical page
    :param reverse: 是否反向排序（如日式装订）
    :param last_skip: 是否跳过最后一页（如需空白页）
    :return: 页码列表
    """
    total_physical_pages = pages_log * FOLD_PAGE_PER_SQUARE
    numbers = []

    for i in range(pages_log):
        left = start_page + i
        right = start_page + total_physical_pages - 1 - i

        if (i % 2 == 0 and reverse) or (i % 2 == 1 and not reverse):
            numbers.extend([left, right])
        else:
            numbers.extend([right, left])

    if last_skip and numbers:
        idx = 1 if reverse else 0
        numbers[idx] = 0  # 0 表示空白页

    return numbers


def generate_unipage_pages(start_page, total_pages):
    """
    每四页变成4123排列
    """
    output_pages = []
    for i in range(total_pages):
        output_pages.append(start_page + i*4 + 3)
        output_pages.append(start_page + i*4)
        output_pages.append(start_page + i*4 + 1)
        output_pages.append(start_page + i*4 + 2)
    return output_pages


def merge_pages_for_folding(input_pdf_path, output_pdf_path, start_page, total_pages, reverse=False, last_skip=False, no_folding=False, unipage=False):
    """
    将PDF的页面按照折叠方式两两合并为一页。
    (修复了坐标偏移导致的空白页问题，以及尺寸不匹配导致的大小问题)
    """
    if not os.path.exists(input_pdf_path):
        logger.error("输入文件 '%s' 不存在。", input_pdf_path)
        return

    if no_folding:
        page_numbers = list[int](range(start_page, start_page+total_pages*2))
    elif unipage:
        page_numbers = generate_unipage_pages(start_page, int(total_pages/2))
    else:
        page_numbers = generate_fold_pages(
            start_page, total_pages, reverse, last_skip)

    # 页数下标调整 因为原来是从1开始的
    # because PyPDF2 uses 0-based indexing
    page_numbers = [page - 1 for page in page_numbers]

    try:
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        if max(page_numbers) > len(reader.pages):
            logger.error("错误: 请求的页码 (%d) 超出了PDF的总页数 (%d)。",
                         max(page_numbers), len(reader.pages))

        for i in range(0, len(page_numbers), 2):
            page1_num = page_numbers[i]
            page2_num = page_numbers[i + 1]

            # 获取页面对象，如果索引无效则为None（代表空白页）
            p1 = reader.pages[page1_num] if 0 <= page1_num < len(
                reader.pages) else None
            p2 = reader.pages[page2_num] if 0 <= page2_num < len(
                reader.pages) else None

            # --- 1. 确定基准尺寸 ---
            # 优先取左页尺寸，如果没有左页则取右页，都为None则跳过
            ref_page = p1 if p1 else p2
            if not ref_page:
                continue

            # 使用 cropbox 获取真实的可见区域尺寸 (解决部分页面看起来很小或留白过多的问题)
            # float() 转换是为了防止 decimal 类型报错
            base_w = float(ref_page.cropbox.width)
            base_h = float(ref_page.cropbox.height)

            # 创建新的空白页：宽度 x 2，高度保持基准高度
            new_page = writer.add_blank_page(width=base_w * 2, height=base_h)

            # --- 2. 定义合并辅助函数 (包含坐标归一化和缩放) ---
            def merge_page_content(target_page, source_page, x_offset, target_h):
                if not source_page:
                    return

                # 获取源页面的起始坐标 (解决内容跑偏/空白的关键)
                src_x = float(source_page.cropbox.left)
                src_y = float(source_page.cropbox.bottom)
                src_w = float(source_page.cropbox.width)
                src_h = float(source_page.cropbox.height)

                # 计算缩放比例：如果源页面高度与基准高度差异超过 1%，则进行缩放
                scale_factor = 1.0
                if abs(src_h - target_h) > target_h * 0.01:
                    scale_factor = target_h / src_h

                # 构建变换矩阵
                # 1. translate(-src_x, -src_y): 将页面内容移回 (0,0) 原点 -> 解决空白页
                # 2. scale(scale_factor): 缩放至匹配高度 -> 解决页面忽大忽小
                # 3. translate(x_offset, 0): 移到目标位置 (左边还是右边)

                # 注意：pypdf 的变换顺序通常是从右向左应用，或者逻辑上的叠加
                tf = Transformation().translate(tx=-src_x, ty=-src_y).scale(sx=scale_factor,
                                                                            sy=scale_factor).translate(tx=x_offset, ty=0)

                # 如果缩放导致宽度溢出半边，可以考虑居中 (这里暂不做复杂居中，默认靠左/靠中线)
                # 简单的居中修正(可选):
                # final_w = src_w * scale_factor
                # center_adjust = (base_w - final_w) / 2
                # tf = tf.translate(tx=center_adjust, ty=0)

                target_page.merge_transformed_page(source_page, tf)

            # --- 3. 执行合并 ---

            # 处理左页 (放在 x=0 处)
            if p1:
                try:
                    merge_page_content(new_page, p1, 0, base_h)
                except Exception as e:
                    logger.warning("合并左页 %d 失败: %s", page1_num, e)

            # 处理右页 (放在 x=base_w 处)
            if p2:
                try:
                    merge_page_content(new_page, p2, base_w, base_h)
                except Exception as e:
                    logger.warning("合并右页 %d 失败: %s", page2_num, e)

        # 写入文件
        with open(output_pdf_path, "wb") as output_file:
            writer.write(output_file)
        logger.info("成功创建: '%s'", output_pdf_path)

    except Exception as e:
        import traceback
        logger.error("处理PDF错误: %s", e)
        logger.error(traceback.format_exc())


def get_pdf_total_pages(file_name):
    """获取PDF文件的总页数"""
    with open(file_name, "rb") as f:
        reader = PdfReader(f)
        return len(reader.pages)


def add_blank_pages_to_pdf(input_pdf_path, output_pdf_path, num_blank_pages):
    """向PDF添加指定数量的空白页"""
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    source_page_count = len(reader.pages)

    # 复制所有现有页面 剥离最后一页 确保变换后最后一页仍然是最后一页
    for page_num in range(source_page_count-1):
        writer.add_page(reader.pages[page_num])

    # 获取页面尺寸
    if len(reader.pages) > 0:
        page_width = reader.pages[0].cropbox.width         # pylint: disable=E1101
        page_height = reader.pages[0].cropbox.height       # pylint: disable=E1101
    else:
        page_width = 595  # A4宽度
        page_height = 842  # A4高度

    # 添加空白页并在其中添加居中文字
    for _ in range(num_blank_pages):
        # 创建一个内存中的PDF文件，用于生成包含文本的空白页
        packet = BytesIO()

        # 创建一个Canvas对象，设置页面大小
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))

        # 在空白页上添加居中文字
        text = "Page for blank."

        # 设置字体和大小
        c.setFont("Helvetica", 12)

        # 计算文本宽度并居中
        text_width = c.stringWidth(text, "Helvetica", 12)
        text_x = (page_width - text_width) / 2
        text_y = page_height / 2

        # 添加文本
        c.drawString(text_x, text_y, text)

        # 保存Canvas
        c.save()

        # 重置 BytesIO 指针到开头
        packet.seek(0)

        # 读取生成的PDF
        text_pdf = PdfReader(packet)
        text_page = text_pdf.pages[0]

        # 将包含文本的页面添加到 writer
        writer.add_page(text_page)

    # 添加最后一页
    if source_page_count > 0:
        writer.add_page(reader.pages[-1])
    # 写入新文件
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

    return output_pdf_path


def process_single_part(file_name, output_filename, start_page, one_side_phy_page_num, last_skip, no_folding):
    """处理单个部分的PDF合并"""
    merge_pages_for_folding(file_name, output_filename, start_page, one_side_phy_page_num,
                            last_skip=last_skip, no_folding=no_folding, unipage=False)


def process_pdf_for_folding(file_name="", split_page_num=80, output_path: str | None = None, no_folding=False, unipage=False):
    if file_name == "":
        file_name = input("请输入PDF文件路径: ")

    file_name = file_name.strip('"\'')

    # 检查文件是否存在
    if not os.path.exists(file_name):
        logger.error("文件 '%s' 不存在。", file_name)
        return

    # get total page
    total_page = get_pdf_total_pages(file_name)
    logger.info("总页数: %d", total_page)

    # 检查是否为4的整数倍，如果不是则添加空白页
    if total_page % 4 != 0:
        blank_pages_needed = 4 - (total_page % 4)
        logger.info("总页数不是4的整数倍，需要添加 %d 个空白页", blank_pages_needed)

        # 创建临时文件名
        temp_file = file_name.replace(".pdf", "_temp_with_blanks.pdf")

        # 添加空白页
        add_blank_pages_to_pdf(file_name, temp_file, blank_pages_needed)

        # 递归调用process_pdf_for_folding处理新文件
        logger.info("使用添加空白页后的文件递归处理...")
        process_pdf_for_folding(temp_file, split_page_num,
                                output_path, no_folding, unipage)

        # 删除临时文件（可选，或者保留供用户检查）
        try:
            os.remove(temp_file)
            logger.info("已删除临时文件")
        except OSError as e:
            logger.warning("警告：无法删除临时文件，请手动删除：%s, errinfo: %s", temp_file, e)
        return

    if output_path is None:
        modified_filename = file_name.replace(".pdf", "_modified_(index).pdf")
    else:
        modified_filename = output_path.replace(
            ".pdf", "_modified_(index).pdf")

    if total_page > split_page_num and not unipage:
        with concurrent.futures.ProcessPoolExecutor(max_workers=(os.cpu_count() if os.cpu_count() else 1)) as executor:
            futures = []
            for i in range(1, total_page + 1, split_page_num):
                end_page = min(i + split_page_num, total_page)
                page_num = end_page - i
                part_index = (i - 1) // split_page_num + 1

                one_side_phy_page_num = int(
                    page_num/2) if page_num % 2 == 0 else int(page_num/2)+1
                output_filename = modified_filename.replace(
                    "(index)", f"{part_index}")
                future = executor.submit(
                    process_single_part, file_name, output_filename, i, one_side_phy_page_num, False, no_folding)
                futures.append(future)

            # 等待所有任务完成
            for future in concurrent.futures.as_completed(futures):
                future.result()
    else:
        # 修复参数传递
        last_skip = False
        one_side_phy_page_num = int(total_page/2) + \
            1 if last_skip else int(total_page/2)
        merge_pages_for_folding(
            file_name,
            modified_filename.replace("_(index)", ""),
            1,
            one_side_phy_page_num,
            last_skip=False,
            no_folding=no_folding,
            unipage=unipage
        )


if __name__ == "__main__":
    import sys
    import logging

    # 配置日志记录器
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    if len(sys.argv) > 2:
        file_name = sys.argv[1]
        output_path = sys.argv[2]
        process_pdf_for_folding(file_name, output_path=output_path)
    else:
        logger.error("Usage: python two_page.py <input_pdf> <output_pdf>")
