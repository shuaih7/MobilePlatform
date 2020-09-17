import tensorflow as tf
from blocks import activation_blocks


__all__ = ["unet_input_block"]


def unet_input_block(
        inputs,
        filters,
        data_format='NCHW',
        is_training=True,
        conv2d_hparams=None,
):
    """

    :param inputs:
    :param filters:
    :param data_format:
    :param is_training:
    :param conv2d_hparams:
    :param block_name:
    :return:
    """
    x = tf.keras.layers.Conv2D(
        filters=filters,
        kernel_size=(3, 3),
        strides=(1, 1),
        padding='same',
        data_format=data_format,
        use_bias=True,
        trainable=is_training,
        kernel_initializer=conv2d_hparams.kernel_initializer,
        bias_initializer=conv2d_hparams.bias_initializer,
    )(inputs)

    x = activation_blocks.activation_block(
        inputs=x,
        act_fn=conv2d_hparams.activation_fn,
        trainable=is_training,
    )

    x = tf.keras.layers.Conv2D(
        filters=filters,
        kernel_size=(3, 3),
        strides=(1, 1),
        padding='same',
        data_format=data_format,
        use_bias=True,
        trainable=is_training,
        kernel_initializer=conv2d_hparams.kernel_initializer,
        bias_initializer=conv2d_hparams.bias_initializer
    )(x)

    x = activation_blocks.activation_block(
        inputs=x,
        act_fn=conv2d_hparams.activation_fn,
        trainable=is_training
    )

    outputs = tf.keras.layers.MaxPooling2D(
        pool_size=(2, 2),
        strides=(2, 2),
        padding='valid',
        data_format=data_format,
    )(x)

    return outputs, x


