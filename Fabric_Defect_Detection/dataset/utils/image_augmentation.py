import tensorflow as tf
import numpy as np


IMAGE_SIZE = 512
AUGMENT_PERCENT = 0.6


def random_flip(image, mask):
    """
    Horizontal and vertical flip
    :param image:
    :param mask:
    :return:
    """
    horizontal_flip = tf.random.uniform(shape=()) > 0.5
    image = tf.cond(
        horizontal_flip,
        lambda: tf.image.flip_left_right(image),
        lambda: image
    )
    mask = tf.cond(
        horizontal_flip,
        lambda: tf.image.flip_left_right(mask),
        lambda: mask
    )

    # vertical flip
    vertical_flip = tf.random.uniform(shape=()) > 0.5
    image = tf.cond(
        vertical_flip,
        lambda: tf.image.flip_up_down(image),
        lambda: image
    )
    mask = tf.cond(
        vertical_flip,
        lambda: tf.image.flip_up_down(mask),
        lambda: mask
    )

    return image, mask


def random_color(
        image,
        brightness_max_delta=0.2,
        contrast_lower=0.9,
        contrast_upper=1.1,
        augment_percent=0.6
):
    """
    Including brightness, contrast, gamma
    """
    image_color_adjusted = image
    # random brightness
    image_color_adjusted = tf.image.random_brightness(image_color_adjusted, max_delta=brightness_max_delta)

    # random contrast
    image_color_adjusted = tf.image.random_contrast(image_color_adjusted, lower=contrast_lower, upper=contrast_upper)

    # random gamma
    # gamma = np.random.uniform(low=0.8, high=1.2, size=[1, ])
    # gain = np.random.uniform(low=0, high=1, size=[1, ])
    # gamma = tf.random.uniform(shape=[], minval=0.9, maxval=1.1, dtype=tf.float32)
    # gain = tf.random.uniform(shape=[], minval=0.9, maxval=1., dtype=tf.float32)
    # image_color_adjusted = tf.image.adjust_gamma(image_color_adjusted, gamma=gamma, gain=gain)

    image_augment_choice = tf.random.uniform(shape=()) < augment_percent

    return tf.cond(image_augment_choice, lambda: image_color_adjusted, lambda: image)


def random_zoom(image, mask, zoom_delta=0.1, augment_percent=0.6):

    box = np.zeros((1, 4))
    x1 = y1 = np.random.uniform(0, zoom_delta)
    x2 = y2 = np.random.uniform(1 - zoom_delta, 1)
    box[0] = [x1, y1, x2, y2]

    def random_crop(img, msk):
        # Create different crops for an image
        img_crop = tf.image.crop_and_resize(
            [img],
            boxes=box,
            box_indices=np.zeros(1),
            crop_size=(IMAGE_SIZE, IMAGE_SIZE)
        )
        msk_crop = tf.image.crop_and_resize(
            [msk],
            boxes=box,
            box_indices=np.zeros(1),
            crop_size=(IMAGE_SIZE, IMAGE_SIZE)
        )
        return img_crop[0], msk_crop[0]

    image_augment_choice = np.random.uniform(low=0.0, high=1.0, size=None)

    if image_augment_choice < augment_percent:
        return random_crop(image, mask)
    else:
        return image, mask


def random_quality(image, mask, augment_percent=0.6):
    image_low_quality = image
    mask_low_quality = mask

    scale = tf.random.uniform(shape=[], minval=0.8, maxval=1.2, dtype=tf.float32)
    image_low_quality = tf.image.resize(image_low_quality, [int(IMAGE_SIZE * scale), int(IMAGE_SIZE * scale)], method='area')
    image_low_quality = tf.image.resize(image_low_quality, [IMAGE_SIZE, IMAGE_SIZE], method='area')

    mask_low_quality = tf.image.resize(mask_low_quality, [int(IMAGE_SIZE * scale), int(IMAGE_SIZE * scale)], method='area')
    mask_low_quality = tf.image.resize(mask_low_quality, [IMAGE_SIZE, IMAGE_SIZE], method='area')

    image_augment_choice = np.random.uniform(low=0.0, high=1.0, size=None)

    if image_augment_choice < augment_percent:
        return image_low_quality, mask_low_quality
    else:
        return image, mask
