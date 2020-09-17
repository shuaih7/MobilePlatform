import numpy as np
from PIL import Image
import os


def concat_image(images, mode="L"):
    if not isinstance(images, list):
        raise Exception('images must be a list')
    count = len(images)
    size = Image.fromarray(images[0]).size
    target = Image.new(mode, (size[0] * count, size[1] * 1))
    for i in range(count):
        image = Image.fromarray(images[i]).resize(size, Image.BILINEAR)
        target.paste(image, (i*size[0], 0, (i+1)*size[0], size[1]))
    return target


def visualize(img_batch, label_pixel_batch, mask_batch, save_dir="./visualization"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for i in range(len(img_batch)):
        mask = np.array(mask_batch[i]).squeeze() * 255
        image = np.array(img_batch[i]).squeeze() * 255
        label_pixel = np.array(label_pixel_batch[i]).squeeze() * 255
        img_visual = concat_image([image, label_pixel, mask])
        visualization_path = os.path.join(save_dir, str(i) + '.jpg')
        img_visual.save(visualization_path)