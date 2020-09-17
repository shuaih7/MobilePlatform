import tensorflow as tf


__all__ = ["regularization_l2loss", "reconstruction_l2loss", "reconstruction_cross_entropy", "adaptive_loss", "AdaptiveLoss"]


def regularization_l2loss(weight_decay):
    """

    :param weight_decay:
    :return:
    """
    pass


def reconstruction_l2loss(y_pred, y_true):
    """

    :param y_pred:
    :param y_true:
    :return:
    """
    reconstruction_err = tf.subtract(y_pred, y_true)
    return tf.reduce_mean(tf.nn.l2_loss(reconstruction_err))


def reconstruction_cross_entropy(y_pred, y_true, from_logits=False):
    return tf.reduce_mean(tf.keras.losses.binary_crossentropy(y_true=y_true, y_pred=y_pred, from_logits=from_logits))


def dice_coe(y_pred, y_true, loss_type='jaccard', smooth=1.):
    """

    :param y_pred: A distribution with shape: [batch_size, ....], (any dimensions)
    :param y_true: The target distribution, format the same with `output`
    :param loss_type: ``jaccard`` or ``sorensen``, default is ``jaccard``
    :param smooth:
    :return:
    """
    y_true_f = tf.keras.layers.Flatten()(y_true)
    y_pred_f = tf.keras.layers.Flatten()(y_pred)

    intersection = tf.reduce_sum(y_true_f * y_pred_f)

    if loss_type == 'jaccard':
        union = tf.reduce_sum(tf.square(y_pred_f)) + tf.reduce_sum(tf.square(y_true_f))

    elif loss_type == 'sorensen':
        union = tf.reduce_sum(y_pred_f) + tf.reduce_sum(y_true_f)

    else:
        raise ValueError("Unknown `loss_type`: %s" % loss_type)

    return (2. * intersection + smooth) / (union + smooth)


def adaptive_loss(y_pred, y_pred_logits, y_true, switch_at_threshold=0.3, loss_type='jaccard'):
    """

    :param y_pred:
    :param y_pred_logits:
    :param y_true:
    :param switch_at_threshold:
    :param loss_type:
    :return:
    """
    dice_loss = 1 - dice_coe(y_pred=y_pred, y_true=y_true, loss_type=loss_type, smooth=1.)

    return tf.cond(
        dice_loss < switch_at_threshold,
        true_fn=lambda: dice_loss,
        false_fn=lambda: reconstruction_cross_entropy(y_pred=y_pred_logits, y_true=y_true, from_logits=True)
    )


class AdaptiveLoss(tf.keras.losses.Loss):
    def __init__(
            self,
            switch_at_threshold=0.3,
            loss_type='jaccard',
            name='adaptive_loss'
    ):
        """

        :param switch_at_threshold:
        :param loss_type:
        """
        super(AdaptiveLoss, self).__init__(name=name)
        self.switch_at_threshold = switch_at_threshold
        self.loss_type = loss_type

    def call(self, y_true, y_pred):
        """

        :param y_true:
        :param y_pred: logits
        :return:
        """
        y_pred_logits = y_pred
        y_pred = tf.math.sigmoid(y_pred_logits)
        dice_loss = 1 - dice_coe(y_pred=y_pred, y_true=y_true, loss_type=self.loss_type, smooth=1.)

        return tf.cond(
            dice_loss < self.switch_at_threshold,
            true_fn=lambda: dice_loss,
            false_fn=lambda: reconstruction_cross_entropy(y_pred=y_pred_logits, y_true=y_true, from_logits=True)
        )

