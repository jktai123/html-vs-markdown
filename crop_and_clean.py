#!/usr/bin/env python3
import os
from PIL import Image
from pathlib import Path

DARK_THRESHOLD = 45
FADE_THRESHOLD = 80

def clean_image(img):
    """套用亮度去背演算法"""
    img = img.convert("RGBA")
    data = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = data[x, y]
            lum = r * 0.299 + g * 0.587 + b * 0.114
            if lum < DARK_THRESHOLD:
                data[x, y] = (r, g, b, 0)
            elif lum < FADE_THRESHOLD:
                ratio = (lum - DARK_THRESHOLD) / (FADE_THRESHOLD - DARK_THRESHOLD)
                data[x, y] = (r, g, b, int(a * ratio))
    return img

def crop_sheet(sheet_path, num_icons, output_names):
    sheet_path = Path(sheet_path)
    if not sheet_path.exists():
        print(f"找不到總表檔案: {sheet_path}")
        return

    print(f"正在處理總表 {sheet_path.name}，預計裁切為 {num_icons} 個圖標...")
    img = Image.open(sheet_path).convert("RGBA")
    w, h = img.size

    for i, name in enumerate(output_names):
        x0 = i * (w // num_icons)
        x1 = (i + 1) * (w // num_icons) if i < num_icons - 1 else w
        col_w = x1 - x0
        
        # 以中間正方形進行裁切
        sq = min(col_w, h)
        cx, cy = x0 + col_w // 2, h // 2
        crop_box = (cx - sq // 2, cy - sq // 2, cx + sq // 2, cy + sq // 2)
        
        crop = img.crop(crop_box)
        crop = crop.resize((256, 256), Image.Resampling.LANCZOS)
        
        # 去背
        cleaned = clean_image(crop)
        
        # 儲存
        out_path = sheet_path.parent / f"{name}.png"
        cleaned.save(out_path)
        print(f"  -> 已產生去背圖標: {out_path.name}")

def main():
    images_dir = Path("images")
    
    # 1. 處理優勢圖標總表 (4 個圖標)
    crop_sheet(
        images_dir / "icons_adv_sheet.png", 
        4, 
        ["icon_chart", "icon_palette", "icon_lightning", "icon_link"]
    )
    
    # 2. 處理其他圖標總表 (3 個圖標)
    crop_sheet(
        images_dir / "icons_other_sheet.png", 
        3, 
        ["icon_trophy", "icon_clipboard", "icon_globe"]
    )

if __name__ == "__main__":
    main()
