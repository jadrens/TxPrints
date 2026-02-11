import os
import sys
import shutil
from logger import default_logger as logger


def move_input_to_cache():
    """将input文件夹中的所有文件移动到cache文件夹"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义文件夹路径
    input_folder = os.path.join(script_dir, "input")
    cache_folder = os.path.join(script_dir, "cache")
    
    # 检查input文件夹是否存在
    if not os.path.exists(input_folder):
        logger.error(f"输入文件夹 '{input_folder}' 不存在。")
        return
    
    # 创建cache文件夹（如果不存在）
    if not os.path.exists(cache_folder):
        os.makedirs(cache_folder)
        logger.info(f"已创建缓存文件夹：{cache_folder}")
    
    # 获取input文件夹中的所有文件
    files = os.listdir(input_folder)
    
    if not files:
        logger.warning("输入文件夹中没有找到文件。")
        return
    
    moved_count = 0
    for file in files:
        src_path = os.path.join(input_folder, file)
        dst_path = os.path.join(cache_folder, file)
        
        try:
            shutil.move(src_path, dst_path)
            logger.info(f"已移动文件: {file}")
            moved_count += 1
        except Exception as e:
            logger.error(f"移动文件 '{file}' 时出错：{e}")
    
    logger.info(f"共移动了 {moved_count} 个文件到缓存文件夹。")


def clean_output_folder():
    """清理output文件夹中的所有文件"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义output文件夹路径
    output_folder = os.path.join(script_dir, "output")
    
    # 检查output文件夹是否存在
    if not os.path.exists(output_folder):
        logger.warning(f"输出文件夹 '{output_folder}' 不存在。")
        return
    
    # 获取output文件夹中的所有文件和文件夹
    items = os.listdir(output_folder)
    
    if not items:
        logger.info("输出文件夹已经是空的。")
        return
    
    deleted_count = 0
    for item in items:
        item_path = os.path.join(output_folder, item)
        
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                logger.info(f"已删除文件: {item}")
                deleted_count += 1
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logger.info(f"已删除文件夹: {item}")
                deleted_count += 1
        except Exception as e:
            logger.error(f"删除 '{item}' 时出错：{e}")
    
    logger.info(f"共删除了 {deleted_count} 个项目。")


def main():
    """主函数，根据命令行参数执行相应操作"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python file_manager.py archive   - 将input文件夹中的文件移动到cache文件夹")
        print("  python file_manager.py clean   - 清理output文件夹中的所有文件")
        return
    
    action = sys.argv[1].lower()
    
    if action == "archive":
        move_input_to_cache()
    elif action == "clean":
        clean_output_folder()
    else:
        logger.error(f"未知的操作: {action}")


if __name__ == "__main__":
    main()