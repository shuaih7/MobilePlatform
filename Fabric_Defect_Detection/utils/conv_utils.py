# Couldn't find conv_utils in TF2.
# Copy and paste deconv_output_length source code from
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/keras/utils/conv_utils.py


def deconv_output_length(
        input_length,
        filter_size,
        padding,
        output_padding=None,
        stride=0,
        dilation=1
):
    """Determines output length of a transposed convolution given input length.
    Arguments:
        input_length: Integer.
        filter_size: Integer.
        padding: one of `"same"`, `"valid"`, `"full"`.
        output_padding: Integer, amount of padding along the output dimension. Can be set to `None` in which case the output length is inferred.
        stride: Integer.
        dilation: Integer.
    Returns:
      The output length (integer).
    """
    assert padding in {'same', 'valid', 'full'}
    if input_length is None:
        return None

    # Get the dilated kernel size
    filter_size = filter_size + (filter_size - 1) * (dilation - 1)

    # Infer length if output padding is None, else compute the exact length
    if output_padding is None:
        if padding == 'valid':
            length = input_length * stride + max(filter_size - stride, 0)
        elif padding == 'full':
            length = input_length * stride - (stride + filter_size - 2)
        elif padding == 'same':
            length = input_length * stride

    else:
        if padding == 'same':
            pad = filter_size // 2
        elif padding == 'valid':
            pad = 0
        elif padding == 'full':
            pad = filter_size - 1

        length = ((input_length - 1) * stride + filter_size - 2 * pad + output_padding)
    return length
