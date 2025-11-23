from lib import g

def pin_image_save(img, filename):
    img_filepath = f'{g.pinterest_tmp_image_folderpath}/images/{filename}.jpg'
    img.save(img_filepath, format='JPEG', subsampling=0, quality=100,)
    return img_filepath

def pin_text_to_lines(text, font, max_w):
    lines = []
    line = ''
    for word in text.split():
        _, _, word_w, word_h = font.getbbox(word)
        _, _, line_w, line_h = font.getbbox(line.strip())
        if  line_w + word_w < max_w:
            line += f'{word} '
        else:
            lines.append(line.strip())
            line = f'{word} '
    if line.strip() != '':
        lines.append(line.strip())
    return lines

