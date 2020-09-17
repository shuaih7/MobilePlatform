import os
import glob
from utils.split_image import split_image


if __name__ == '__main__':
    # img_path = '../dataset/oih_stitch_skipping_anomaly_detection/abnormal/MER-502-79U3M(NR0190090349)_2019-12-27_12_08_18_154-241.PNG'
    save_path = '../dataset/oih_stitch_skipping_anomaly_detection/abnormal_split_512'

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # glob all images
    root = '../dataset/oih_stitch_skipping_anomaly_detection/image'
    images = []
    images += glob.glob(os.path.join(root, '*.PNG'))
    images.sort()

    print(len(images))
    print(images)

    for image in images:
        split_image(image, save_path, overlap=0)