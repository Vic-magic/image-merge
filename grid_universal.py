"""
通用图片拼接脚本 —— 支持任意行列数（3×3, 4×4, 5×2 ……）

使用说明：
  1. 把要拼接的图片放在与本脚本相同的文件夹下
  2. 修改下方 ★ 可调参数 ★ 区域中的 ROWS、COLS、FILES 等
  3. 运行：python grid_universal.py
  4. 结果默认保存为 grid_result.png

依赖：pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ============================================================
# ★ 可调参数 ★  所有参数都在这里，改值即可，无需改动下方代码
# ============================================================

# ── 网格尺寸 ──────────────────────────────────────────────
ROWS = 3            # 行数（你想几行就写几，如 2, 3, 4, 5...）
COLS = 3            # 列数（你想几列就写几，如 2, 3, 4, 5...）
                    # 注意：len(FILES) 必须 == ROWS × COLS

# ── 图片文件列表（按行排列：第1行从左到右 → 第2行从左到右 → ...）──
# 支持 .png / .jpg / .tif 等 Pillow 能打开的格式
FILES = [
    # 第1行
    "img01.png", "img02.png", "img03.png",
    # 第2行
    "img04.png", "img05.png", "img06.png",
    # 第3行
    "img07.png", "img08.png", "img09.png",
]

# ── 布局间距 ──────────────────────────────────────────────
GAP_X = 20          # 水平间距（像素），即左右两张图之间的空白宽度，≥0
GAP_Y = 30          # 垂直间距（像素），即上下两行之间的空白高度，≥0

# ── 背景 ──────────────────────────────────────────────────
BG_COLOR = (255, 255, 255, 255)   # 背景色，RGBA：(红, 绿, 蓝, 透明度)
                                   # 每项 0~255，白色=(255,255,255,255)

# ── 编号标签 ──────────────────────────────────────────────
# 是否为每张子图添加编号，如 (a) (b) (c) ...
LABEL_ENABLE = True

# 字体文件路径（Windows 系统自带 Times New Roman 粗体）
LABEL_FONT_PATH = r"C:/Windows/Fonts/timesbd.ttf"
# 备选字体参考（取消注释即可换）：
# LABEL_FONT_PATH = r"C:/Windows/Fonts/times.ttf"          # 常规体
# LABEL_FONT_PATH = r"C:/Windows/Fonts/arialbd.ttf"        # Arial 粗体

LABEL_FONT_SIZE = 72   # 字号（像素），越大字越大

# 标签在每张图片左上角的偏移量（像素），以该图片左上角为原点 (0,0)
LABEL_OFFSET_X = 25    # X 偏移：正值=向右移，负值=向左移
LABEL_OFFSET_Y = 15    # Y 偏移：正值=向下移，负值=向上移

# 标签颜色，RGBA 格式
LABEL_COLOR = (0, 0, 0, 255)        # 黑色（默认）
# LABEL_COLOR = (255, 255, 255, 255)  # 白色（适合深色背景）

# 编号样式
#   LABEL_FORMAT = "({letter})"   → 输出 "(a)", "(b)", "(c)" ...
#   LABEL_FORMAT = "{letter}"     → 输出 "a", "b", "c" ...
#   LABEL_FORMAT = "({letter}) "  → 输出 "(a) ", "(b) ", "(c) " ...
LABEL_FORMAT = "({letter})"

# 编号起始序号：1=a, 2=b, ..., 26=z
# 如需中途接续前面的编号，改这个值即可（如前面排到(f)，这里填7就从(g)开始）
LABEL_START_INDEX = 1

# ── 输出文件名 ────────────────────────────────────────────
OUTPUT_NAME = "grid_result.png"     # 保存的文件名（放在脚本同目录下）

# ── 单元格对齐方式 ────────────────────────────────────────
# 每张图片在其单元格内的对齐方式：
#   "center"  = 居中（默认，最常用）
#   "top-left" = 左上角对齐
ALIGN = "center"

# ============================================================
# 以下为拼接逻辑，通常无需修改
# ============================================================

def get_cell_position(r, c, cell_w, cell_h, img_w, img_h):
    """
    计算图片在单元格内的 (x, y) 坐标。

    参数
    ----
    r, c       : 当前行号和列号（从0开始）
    cell_w, cell_h : 单元格宽高（所有单元格尺寸一致，取最大图宽高）
    img_w, img_h   : 当前图片的实际宽高

    返回
    ----
    (x, y) : 图片左上角在画布上的绝对坐标
    """
    # 单元格左上角在画布上的绝对位置
    cell_left = c * (cell_w + GAP_X)
    cell_top  = r * (cell_h + GAP_Y)

    if ALIGN == "center":
        # 居中：单元格中心对齐图片中心
        x = cell_left + (cell_w - img_w) // 2
        y = cell_top  + (cell_h - img_h) // 2
    else:
        # 左上角对齐
        x = cell_left
        y = cell_top

    return x, y


def main():
    # --- 1. 路径设置 ---
    # os.path.dirname(os.path.abspath(__file__)) = 本脚本所在目录
    dir_path = os.path.dirname(os.path.abspath(__file__))

    # --- 2. 参数校验 ---
    expected = ROWS * COLS
    if len(FILES) != expected:
        raise ValueError(
            f"FILES 数量 ({len(FILES)}) 与 ROWS×COLS ({ROWS}×{COLS}={expected}) 不匹配！\n"
            f"请确保 FILES 列表恰好有 {expected} 个文件名。"
        )

    # --- 3. 加载所有图片 ---
    images = {}  # {文件名: PIL.Image 对象}
    for fn in FILES:
        fp = os.path.join(dir_path, fn)
        if not os.path.exists(fp):
            raise FileNotFoundError(f"找不到文件: {fn}\n请确认文件在脚本同目录下且拼写正确。")
        images[fn] = Image.open(fp)
        print(f"  [OK] {fn}  ({images[fn].width}x{images[fn].height})")

    # --- 4. 计算单元格尺寸（所有格子一样大，取最大宽高）---
    cell_w = max(im.width  for im in images.values())
    cell_h = max(im.height for im in images.values())

    # 画布总尺寸 = 单元格数 × 单元格尺寸 + 间距空隙
    canvas_w = cell_w * COLS + GAP_X * (COLS - 1)
    canvas_h = cell_h * ROWS + GAP_Y * (ROWS - 1)

    print(f"\n  网格: {ROWS}行 × {COLS}列")
    print(f"  单元格: {cell_w}×{cell_h} px")
    print(f"  间距: 水平{GAP_X}px / 垂直{GAP_Y}px")
    print(f"  画布: {canvas_w}×{canvas_h} px")

    # --- 5. 创建空白画布 ---
    canvas = Image.new("RGBA", (canvas_w, canvas_h), BG_COLOR)

    # --- 6. 准备字体和绘图对象 ---
    if LABEL_ENABLE:
        try:
            font = ImageFont.truetype(LABEL_FONT_PATH, LABEL_FONT_SIZE)
            print(f"  字体: {LABEL_FONT_PATH}  {LABEL_FONT_SIZE}px")
        except OSError:
            print(f"  [WARN] Font not found: {LABEL_FONT_PATH}, using default")
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(canvas)
        # 字母表：a~z 供26个编号，超出26个则用数字
        alphabet = "abcdefghijklmnopqrstuvwxyz"

    # --- 7. 逐单元格拼接 ---
    print()
    for idx, fn in enumerate(FILES):
        r = idx // COLS   # 当前行号（0-based）
        c = idx %  COLS   # 当前列号（0-based）
        im = images[fn]

        # 计算图片在画布上的放置位置
        x, y = get_cell_position(r, c, cell_w, cell_h, im.width, im.height)

        # 粘贴图片（RGBA 模式用自身做 mask 以保留透明通道）
        canvas.paste(im, (x, y), im if im.mode == "RGBA" else None)

        # 添加编号标签
        if LABEL_ENABLE:
            # 计算编号字母
            letter_idx = LABEL_START_INDEX - 1 + idx
            if letter_idx < 26:
                letter = alphabet[letter_idx]
            else:
                # 超出 a~z 范围则用数字编号
                letter = str(letter_idx + 1)

            label_text = LABEL_FORMAT.replace("{letter}", letter)
            lx = x + LABEL_OFFSET_X
            ly = y + LABEL_OFFSET_Y
            draw.text((lx, ly), label_text, fill=LABEL_COLOR, font=font)
            print(f"  [{r},{c}] {label_text}  ← {fn}")
        else:
            print(f"  [{r},{c}] {fn}")

    # --- 8. 保存结果 ---
    output_path = os.path.join(dir_path, OUTPUT_NAME)
    canvas.save(output_path, "PNG", optimize=False)
    print(f"\n  [OK] Saved -> {output_path}")

    # --- 9. 关闭所有图片 ---
    for im in images.values():
        im.close()


if __name__ == "__main__":
    main()
