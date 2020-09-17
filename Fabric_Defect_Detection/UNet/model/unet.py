import tensorflow as tf
from blocks import *
from hparams import *


class UNet:
    def __init__(
            self,
            compute_format,
            input_format,
            n_output_channels,
            unet_variant,
            activation_fn,
            weight_init_method,
    ):
        if unet_variant == "original":  # Total Params: 36,950,273
            input_filters = 64
            unet_block_filters = [128, 256, 512]
            bottleneck_filters = 1024
            output_filters = 64

        elif unet_variant == "tinyUNet":  # Total Params: 1,824,945
            input_filters = 32
            unet_block_filters = [32, 64, 128]
            bottleneck_filters = 256
            output_filters = 32

        # model hyperparameters
        self.model_hparams = ModelHparams(
            compute_format=compute_format,
            input_format=input_format,
            input_filters=input_filters,
            unet_block_filters=unet_block_filters,
            bottleneck_filters=bottleneck_filters,
            output_filters=output_filters,
            n_output_channels=n_output_channels
        )

        # conv layer hyperparameters
        self.conv2d_hparams = Conv2dHparams(
            kernel_initializer='glorot_uniform',
            bias_initializer='zeros',
            activation_fn=activation_fn
        )

        # if weight_init_method == "he_normal":
        #     self.conv2d_hparams.kernel_initializer = tf.keras.initializers.VarianceScaling(
        #         scale=2.0, distribution='truncated_normal', mode='fan_in'
        #     )
        #
        # elif weight_init_method == "he_uniform":
        #     self.conv2d_hparams.kernel_initializer = tf.keras.initializers.VarianceScaling(
        #         scale=2.0, distribution='uniform', mode='fan_in'
        #     )
        #
        # elif weight_init_method == "glorot_normal":
        #     self.conv2d_hparams.kernel_initializer = tf.keras.initializers.VarianceScaling(
        #         scale=1.0, distribution='truncated_normal', mode='fan_avg'
        #     )
        #
        # elif weight_init_method == "glorot_uniform":
        #     self.conv2d_hparams.kernel_initializer = tf.keras.initializers.VarianceScaling(
        #         scale=1.0, distribution='uniform', mode='fan_avg'
        #     )
        #
        # elif weight_init_method == "orthogonal":
        #     self.conv2d_hparams.kernel_initializer = tf.keras.initializers.Orthogonal(gain=1.0)

        self.model = self._build_model(inputs_shape=(512, 512, 1))

    def _build_model(self, inputs_shape, training=True):
        """
        U-Net: Convolutional Networks for Biomedical Image Segmentation
        :param inputs_shape:
        :param training:
        :return:
        """
        skip_connections = []

        # input layer
        inputs = tf.keras.layers.Input(shape=inputs_shape)

        x, out = unet_input_block(
            inputs,
            filters=self.model_hparams.input_filters,
            data_format=self.model_hparams.compute_format,
            is_training=training,
            conv2d_hparams=self.conv2d_hparams
        )

        skip_connections.append(out)

        # downsample layers
        for idx, filters in enumerate(self.model_hparams.unet_block_filters):
            # net, out = downsample_block(net, filters=filters, idx=idx)

            x, skip_connect = unet_downsample_block(
                x,
                filters=filters,
                data_format=self.model_hparams.compute_format,
                is_training=training,
                conv2d_hparams=self.conv2d_hparams,
            )

            skip_connections.append(skip_connect)

        # print('shape before bottleneck:', x)
        # bottleneck
        x = unet_bottleneck_block(
            x,
            filters=self.model_hparams.bottleneck_filters,
            data_format=self.model_hparams.compute_format,
            is_training=training,
            conv2d_hparams=self.conv2d_hparams,
        )

        # TODO: remove debug
        # print('shape after bottleneck:', x)
        # print(skip_connections)

        # upsample layers
        for idx, filters in enumerate(reversed(self.model_hparams.unet_block_filters)):
            x = unet_upsample_block(
                x,
                residual_input=skip_connections.pop(),
                filters=filters,
                data_format=self.model_hparams.compute_format,
                is_training=training,
                conv2d_hparams=self.conv2d_hparams,
            )

        # output layer
        logits = unet_output_block(
            inputs=x,
            residual_input=skip_connections.pop(),
            filters=self.model_hparams.output_filters,
            n_output_channels=self.model_hparams.n_output_channels,
            data_format=self.model_hparams.compute_format,
            is_training=training,
            conv2d_hparams=self.conv2d_hparams,
        )

        # outputs = tf.keras.activations.sigmoid(logits)
        outputs = logits

        model = tf.keras.Model(inputs, outputs)

        return model


if __name__ == '__main__':
    unet = UNet()
    unet.model.summary()

