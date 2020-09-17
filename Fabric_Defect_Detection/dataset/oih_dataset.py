import tensorflow as tf
import numpy as np
import os
import csv
import shutil
import glob
import random
import cv2
from dataset.utils.image_augmentation import random_zoom, random_color, random_flip, random_quality


def get_masks(root):
    g = os.walk(os.path.join(root, 'labelme_json'))
    for path, dir_list, file_list in g:
        # print(path)
        for file_name in file_list:
            src = os.path.join(path, file_name)
            if file_name == 'img.png':
                name = path.split('/')[-1].split('_')[0]
                dst = os.path.join(root, 'image', name + '.PNG')
                # shutil.copy2(src, dst)

            if file_name == 'label.png':
                name = path.split('/')[-1]
                dst = os.path.join(root, 'mask', name + '_mask.PNG')
                shutil.copy2(src, dst)


def binarize_masks(masks):
    for mask in masks:
        im_gray = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
        thresh = np.amax(im_gray) - 1
        im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
        cv2.imwrite(mask, im_bw)


def load_csv(root, filename):
    if not os.path.exists(os.path.join(root, filename)):
        images, masks = [], []
        images += glob.glob(os.path.join(root, 'image', '*.PNG'))
        masks += glob.glob(os.path.join(root, 'mask', '*.PNG'))
        images.sort()
        masks.sort()
        image_mask = list(zip(images, masks))
        # print dataset information
        # print(len(image_mask), image_mask)
        random.shuffle(image_mask)
        # create csv file
        with open(os.path.join(root, filename), mode='w', newline='') as f:
            writer = csv.writer(f)
            for item in image_mask:
                writer.writerow(item)
        print('written into csv file:', filename)

    # if csv file exists, load it
    images, masks = [], []
    with open(os.path.join(root, filename)) as f:
        reader = csv.reader(f)
        for row in reader:
            image, mask = row
            images.append(image)
            masks.append(mask)

    return images, masks


def load_defect(root, mode='train'):
    # load csv
    # if not mode == 'test':
    #     csv_dir = 'train'
    # else:
    #     csv_dir = 'test'

    images, masks = load_csv(os.path.join(root), 'image_mask.csv')
    if mode == 'train':
        images = images[:int(0.8 * len(images))]
        masks = masks[:int(0.8 * len(masks))]
    elif mode == 'valid':
        images = images[int(0.8 * len(images)):]
        masks = masks[int(0.8 * len(masks)):]
    elif mode == 'test':
        images = images
        masks = masks

    return images, masks


def normalize(input_image, input_mask):
    input_image = tf.cast(input_image, tf.float32) / 255.0
    input_mask = tf.cast(input_mask, tf.float32) / 255.0
    return input_image, input_mask


def preprocess_train(input_image, input_mask):

    input_image = tf.io.read_file(input_image)
    input_image = tf.image.decode_png(input_image, channels=1)

    input_mask = tf.io.read_file(input_mask)
    input_mask = tf.image.decode_png(input_mask, channels=1)
    input_mask = tf.cast(input_mask, tf.float32)

    # augmentation
    # horizontal and vertical flip
    input_image, input_mask = random_flip(input_image, input_mask)

    # brightness, contrast, gamma
    input_image = random_color(input_image)

    # random zoom
    input_image, input_mask = random_zoom(input_image, input_mask)

    # random quality
    # input_image, input_mask = random_quality(input_image, input_mask)

    # # rotate
    # n_rots = tf.random.uniform(shape=(), dtype=tf.int32, minval=0, maxval=3, seed=582)
    # input_image = tf.image.rot90(input_image, k=n_rots)
    # input_mask = tf.image.rot90(input_mask, k=n_rots)

    # normalize
    input_image, input_mask = normalize(input_image, input_mask)

    return input_image, input_mask


def preprocess_test(input_image, input_mask):

    input_image = tf.io.read_file(input_image)
    input_image = tf.image.decode_png(input_image, channels=1)

    input_mask = tf.io.read_file(input_mask)
    input_mask = tf.image.decode_png(input_mask, channels=1)
    input_mask = tf.cast(input_mask, tf.float32)

    # augmentation
    # horizontal and vertical flip
    input_image, input_mask = random_flip(input_image, input_mask)

    # brightness, contrast, gamma
    input_image = random_color(
        input_image,
        brightness_max_delta=0.3,
        contrast_lower=0.85,
        contrast_upper=1.15,
        augment_percent=1.0
    )

    # random zoom
    input_image, input_mask = random_zoom(input_image, input_mask, zoom_delta=0.2, augment_percent=1.0)

    # random quality
    input_image, input_mask = random_quality(input_image, input_mask, augment_percent=1.0)

    # normalize
    input_image, input_mask = normalize(input_image, input_mask)

    return input_image, input_mask


if __name__ == '__main__':
    # root = './oih_stitch_skipping'
    # get_masks(root)

    csv_root = '../dataset/oih_stitch_skipping'
    csv_filename = 'image_mask.csv'
    images, masks = load_defect(csv_root, csv_filename)
    print(images)


