# PDF打印工具

这是一个用于PDF文件处理和打印准备的工具集合，主要用于添加页码、重新排列页面以适应不同的打印需求（如双页装订），以及处理适合不同类型信封的PDF格式。

## 项目结构

- `batch_processor.py` - 命令行工具
- `gui_app.py` - GUI版本（基于PyQt6）
- `custom_module.py` - 核心功能模块
- `tools/` - 具体PDF处理工具实现
- `logger.py` - 日志记录模块
- `mem_disk.py` - 内存盘管理模块（用于提高处理速度）
- `file_manager.py` - 文件管理工具
- `input/` - 输入PDF文件目录
- `output/` - 处理后PDF文件输出目录
- `docs/` - 文档目录

## 功能说明

### 1. 添加页码
- `add_page_number_graph` - 添加图形化页码（带圆圈的自适应大小页码）
- `add_page_number` - 添加简单倒置页码（当前/总页数格式）

### 2. 页面重新排列
- `re_2page_staple` - 重新排列PDF页面以适应双页装订（带折叠）
- `re_2page_nofold` - 重新排列PDF页面以适应双页布局（无折叠）

### 3. 信封适配
- `suit_normal_envelop` - 添加页码并重新排列页面以适应标准信封
- `suit_unifold_envelop` - 添加页码并重新排列页面以适应单折信封

### 4. 文件管理
- `archive` - 将输入文件移动到缓存目录
- `clean/clear` - 清理输出文件夹

## 安装说明

1. 确保安装了Python 3.7+
2. 安装依赖：
   ```
   pip install PyQt6
   ```
3. 确保`input`和`output`目录存在，若不存在会自动创建

## 使用方法

### 命令行工具 (batch_processor.py)

```bash
python batch_processor.py <命令>
```

示例：
```bash
# 添加图形化页码
python batch_processor.py add_page_number_graph

# 重新排列页面以适应双页装订
python batch_processor.py re_2page_staple

# 处理适合标准信封的PDF
python batch_processor.py suit_normal_envelop

# 清理输出文件夹
python batch_processor.py clean
```

### GUI工具 (gui_app.py)

1. 运行GUI应用：
   ```bash
   python gui_app.py
   ```

2. 在界面中选择所需的命令，然后点击"Run"按钮执行

3. 执行结果会显示在下方的输出窗口中

## 注意事项

1. **管理员权限**：
   - 以管理员身份运行时，工具会使用内存盘作为缓冲区，提高处理速度
   - 非管理员身份运行时，会使用临时文件作为缓冲区

2. **文件处理**：
   - 工具会自动处理`input`目录中的所有PDF文件
   - 处理后的文件会保存在`output`目录中，文件名会添加`_processed`后缀

3. **依赖项**：
   - GUI版本需要安装PyQt6
   - 核心功能依赖于`tools`目录中的PDF处理模块

4. **局限性**：
   - 仅支持PDF文件
   - 大型PDF文件可能需要较长的处理时间
   - 部分功能可能需要特定的打印机支持

## 常见问题

- **为什么需要管理员权限？**
  - 管理员权限用于创建和管理内存盘，以提高处理速度，特别是对于大型PDF文件

- **处理后的文件在哪里？**
  - 处理后的文件保存在`output`目录中

- **如何处理多个PDF文件？**
  - 只需将所有PDF文件放入`input`目录，工具会自动处理所有文件

## 版本信息

- 自用工具，不保证维护
- 如有问题，请自行修改代码

## 许可证

本项目仅供个人使用，未指定具体许可证。

---

[English Version](../README.md)
