import tensorflow as tf
import os
import csv
import glob
import random


def load_csv(root, filename):
    if not os.path.exists(os.path.join(root, filename)):
        images = []
        images += glob.glob(os.path.join(root, '*.PNG'))
        images.sort()
        # print dataset information
        # print('===============', len(images), images)
        # images = list(images)
        random.shuffle(images)
        # create csv file
        with open(os.path.join(root, filename), mode='w', newline='') as f:
            writer = csv.writer(f)
            for item in images:
                print(item)
                writer.writerow([item, ])
            # writer.writerows(images)
        print('written into csv file:', filename)

    # if csv file exists, load it
    images = []
    with open(os.path.join(root, filename)) as f:
        reader = csv.reader(f)
        for row in reader:
            image = row
            images.append(image)

    return images


def load_defect(root, mode='train'):
    # load csv
    # if not mode == 'test':
    #     csv_dir = 'train'
    # else:
    #     csv_dir = 'test'

    print('start loading', root)
    images = load_csv(os.path.join(root), 'images.csv')
    if mode == 'train':
        images = images[:int(0.8 * len(images))]
    elif mode == 'valid':
        images = images[int(0.8 * len(images)):]
    elif mode == 'test':
        images = images

    flatten_list_func = lambda x: [y for l in x for y in flatten_list_func(l)] if type(x) is list else [x]
    images = flatten_list_func(images)

    return images


def normalize(input_image):
    """
    Normalize images to [-1, 1]
    :param input_image:
    :return:
    """
    input_image = tf.cast(input_image, tf.float32)
    input_image_max_value = tf.reduce_max(input_image)
    input_image = ((input_image / input_image_max_value) - 0.5) * 2
    return input_image


def preprocess_train(input_image):

    input_image = tf.io.read_file(input_image)
    input_image = tf.image.decode_png(input_image, channels=1)

    # normalize
    input_image = normalize(input_image)

    return input_image


if __name__ == '__main__':
    data_root = '../dataset/oih_stitch_skipping_anomaly_detection'
    images = load_csv(data_root, 'images.csv')
    images = load_defect(data_root)
    print('shape of images:', len(images))
    print(images)
    func = lambda x: [y for l in x for y in func(l)] if type(x) is list else [x]
    result = func(images)
    print(result)