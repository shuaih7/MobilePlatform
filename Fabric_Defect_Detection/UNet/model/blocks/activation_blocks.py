import tensorflow as tf


__all__ = [
    "authorized_activation_fn",
    "activation_block",
]

authorized_activation_fn = ["relu", "leaky_relu", "prelu_shared", "prelu_not_shared", "selu", "crelu", "elu"]


def activation_block(inputs, act_fn, trainable=True):
    """

    :param inputs:
    :param act_fn:
    :param trainable:
    :return:
    """
    if act_fn == "relu":
        return tf.keras.activations.relu(inputs)
        # return tf.keras.activations.relu

    if act_fn == "leaky_relu":
        return tf.keras.activations.leaky_relu(inputs, alpha=0.2)

    if act_fn == "prelu_shared":
        return tf.keras.activations.prelu(inputs, channel_shared=True, trainable=trainable)

    if act_fn == "prelu_not_shared":
        return tf.keras.activations.prelu(inputs, channel_shared=False, trainable=trainable)

    if act_fn == "selu":
        return tf.keras.activations.selu(inputs)

    if act_fn == "crelu":
        return tf.keras.activations.crelu(inputs)

    if act_fn == "elu":
        return tf.keras.activations.elu(inputs)

    raise ValueError("Unknown activation function: %s - Authorized: %s" % (act_fn, authorized_activation_fn))
