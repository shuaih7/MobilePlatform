import tensorflow as tf
from blocks.activation_blocks import activation_block


__all__ = ["unet_upsample_block"]


def unet_upsample_block(
        inputs,
        residual_input,
        filters,
        data_format='NHWC',
        is_training=True,
        conv2d_hparams=None
):
    """

    :param inputs:
    :param residual_input:
    :param filters:
    :param data_format:
    :param is_training:
    :param conv2d_hparams:
    :return:
    """
    # print('upsample concat:', inputs, residual_input)
    x = tf.concat([inputs, residual_input], axis=1 if data_format == 'NCHW' else 3)

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

    x = activation_block(
        inputs=x,
        act_fn=conv2d_hparams.activation_fn,
        trainable=is_training
    )

    x = tf.keras.layers.Conv2D(
        filters=filters // 2,
        kernel_size=(3, 3),
        strides=(1, 1),
        padding='same',
        data_format=data_format,
        use_bias=True,
        trainable=is_training,
        kernel_initializer=conv2d_hparams.kernel_initializer,
        bias_initializer=conv2d_hparams.bias_initializer,
    )(x)

    x = activation_block(
        inputs=x,
        act_fn=conv2d_hparams.activation_fn,
        trainable=is_training
    )

    x = tf.keras.layers.Conv2DTranspose(
        filters=filters // 2,
        kernel_size=(2, 2),
        strides=(2, 2),
        padding='same',
        data_format=data_format,
        use_bias=True,
        trainable=is_training,
        kernel_initializer=conv2d_hparams.kernel_initializer,
        bias_initializer=conv2d_hparams.bias_initializer
    )(x)

    x = activation_block(
        inputs=x,
        act_fn=conv2d_hparams.activation_fn,
        trainable=is_training
    )

    return x


