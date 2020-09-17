import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, Input, MaxPool2D, ReLU, BatchNormalization, Flatten


class AutoEncoder:
    def __init__(
            self,
            image_size=256,
            channels=1,
            latent_size=100,
            base_filters=16,
            conv_layers=4,
    ):
        self.image_size = image_size
        self.channels = channels
        self.latent_size = latent_size
        self.base_filters = base_filters
        self.conv_layers = conv_layers

        # TODO: build model
        self._build_model()

    def _build_model(self):
        inputs = Input(shape=[self.image_size, self.image_size, self.channels])

        # encoder
        filters = self.base_filters
        x = inputs
        for i in range(self.conv_layers):
            x = Conv2D(
                filters=filters,
                kernel_size=3,
                strides=(1, 1),
                padding='same'
            )(x)
            x = ReLU()(x)
            x = MaxPool2D(padding='same')(x)
            filters *= 2

        encoded = x

        # decoder
        for i in range(self.conv_layers):
            filters = filters // 2
            x = Conv2DTranspose(
                filters=filters,
                kernel_size=3,
                strides=(2, 2),
                padding='same'
            )(x)
            x = ReLU()(x)

        # merge all channels
        decoded = Conv2D(filters=1, kernel_size=1, padding='same')(x)

        self.encoder = Model(inputs, encoded)
        self.auto_encoder = Model(inputs, decoded)


if __name__ == '__main__':
    ae = AutoEncoder()
    ae.auto_encoder.summary()



