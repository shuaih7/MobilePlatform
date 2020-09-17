import tensorflow as tf
from blocks import activation_blocks


__all__ = ["unet_output_block"]


def unet_output_block(
    inputs,
    residual_input,
    filters,
    n_output_channels,
    data_format='NHWC',
    is_training=True,
    conv2d_hparams=None,
):
    """

    :param inputs:
    :param residual_input:
    :param filters:
    :param n_output_channels:
    :param data_format:
    :param is_training:
    :param conv2d_hparams:
    :param block_name:
    :return:
    """
    # x = tf.concat([inputs, residual_input], axis=1 if data_format == 'NCHW' else 3)
    # print(inputs, residual_input)
    x = tf.concat([inputs, residual_input], axis=-1)

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

    x = tf.keras.layers.Conv2D(
        filters=n_output_channels,
        kernel_size=(1, 1),
        strides=(1, 1),
        padding='same',
        data_format=data_format,
        use_bias=True,
        trainable=is_training,
        kernel_initializer=conv2d_hparams.kernel_initializer,
        bias_initializer=conv2d_hparams.bias_initializer
    )(x)

    return x