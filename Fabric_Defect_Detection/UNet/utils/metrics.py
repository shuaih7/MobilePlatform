import tensorflow as tf

__all__ = [
    "iou_score",
    "IOUScore"
]


def iou_score(y_pred, y_true, threshold, eps=1e-5):
    """

    :param y_pred:
    :param y_true:
    :param threshold:
    :param eps:
    :return:
    """
    y_true = tf.cast(y_true > threshold, dtype=tf.float32)
    y_pred = tf.cast(y_pred > threshold, dtype=tf.float32)

    intersection = y_true * y_pred
    intersection = tf.reduce_sum(intersection, axis=(1, 2, 3))

    numerator = 2.0 * intersection + eps

    divisor = tf.reduce_sum(y_true, axis=(1, 2, 3)) + tf.reduce_sum(y_pred, axis=(1, 2, 3)) + eps

    return tf.reduce_mean(numerator / divisor)


class IOUScore(tf.keras.metrics.Metric):

    def __init__(self, threshold, eps=1e-5, name='iou_score'):
        super(IOUScore, self).__init__(name=name)
        self.threshold = threshold
        self.eps = eps
        self.iou_score = self.add_weight(name='tp', initializer='zeros')

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_pred = tf.math.sigmoid(y_pred)
        y_true = tf.cast(y_true > self.threshold, dtype=tf.float32)
        y_pred = tf.cast(y_pred > self.threshold, dtype=tf.float32)

        intersection = y_true * y_pred
        intersection = tf.reduce_sum(intersection, axis=(1, 2, 3))

        numerator = 2.0 * intersection + self.eps

        divisor = tf.reduce_sum(y_true, axis=(1, 2, 3)) + tf.reduce_sum(y_pred, axis=(1, 2, 3)) + self.eps

        self.iou_score.assign_add(tf.reduce_mean(numerator / divisor))

    def result(self):
        return self.iou_score

    def reset_states(self):
        # The state of the metric will be reset at the start of each epoch.
        self.iou_score.assign(0.)

