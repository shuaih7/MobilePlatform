import cv2
import os


def start_points(size, split_size, overlap=0):
    if overlap > 1 or overlap < 0:
        raise ValueError('overlab should be in [0, 1]')
    points = [0]
    stride = int(split_size * (1 - overlap))
    counter = 1
    while True:
        pt = stride * counter
        if pt + split_size >= size:
            points.append(size - split_size)
            break
        else:
            points.append(pt)
        counter += 1
    return points


def split_image(
        img_path,
        save_path,
        split_width=64,
        split_height=64,
        overlap=0,
):
    img = cv2.imread(img_path)
    img_h, img_w, _ = img.shape

    x_points = start_points(img_w, split_width, overlap)
    y_points = start_points(img_h, split_height, overlap)

    count = 0
    print(img_path)
    name = img_path.split('/')[-1].split('.')[0]
    print(name)
    format = 'PNG'

    # start to split and save
    for i in y_points:
        for j in x_points:
            split = img[i:i + split_height, j:j + split_width]
            cv2.imwrite(os.path.join(save_path, '{}_{}.{}'.format(name, count, format)), split)
            count += 1


if __name__ == '__main__':
    img_path = '../dataset/oih_stitch_skipping_anomaly_detection/abnormal/MER-502-79U3M(NR0190090349)_2019-12-27_12_08_18_154-241.PNG'
    save_path = '../dataset/oih_stitch_skipping_anomaly_detection/abnormal_split'
    split_image(img_path, save_path, overlap=0.2)