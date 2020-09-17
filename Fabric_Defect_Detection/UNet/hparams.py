class ModelHparams():
    def __init__(
            self,
            input_format=None,  # NCHW or NHWC
            compute_format=None,  # NCHW or NHWC
            n_channels=None,
            activation_fn=None,
            weight_init_method=None,
            model_variant=None,
            input_shape=None,
            mask_shape=None,
            input_normalization_method=None,

            input_filters=None,
            unet_block_filters=None,
            bottleneck_filters=None,
            output_filters=None,
            n_output_channels=None
    ):
        self.input_format = input_format  # NCHW or NHWC
        self.compute_format = compute_format  # NCHW or NHWC
        self.n_channels = n_channels
        self.activation_fn = activation_fn
        self.weight_init_method = weight_init_method
        self.model_variant = model_variant
        self.input_shape = input_shape
        self.mask_shape = mask_shape
        self.input_normalization_method = input_normalization_method

        self.input_filters = input_filters
        self.unet_block_filters = unet_block_filters
        self.bottleneck_filters = bottleneck_filters
        self.output_filters = output_filters
        self.n_output_channels = n_output_channels


class Conv2dHparams:
    def __init__(
            self,
            kernel_initializer=None,
            bias_initializer=None,
            activation_fn=None
    ):
        self.kernel_initializer = kernel_initializer
        self.bias_initializer = bias_initializer
        self.activation_fn = activation_fn