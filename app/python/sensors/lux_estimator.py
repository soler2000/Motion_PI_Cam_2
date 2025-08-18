# Very rough "lux" from grayscale mean (0-255 -> 0..100)
def pseudo_lux(gray_mean):
    return int((gray_mean/255.0)*100)
