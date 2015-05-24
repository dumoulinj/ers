import numpy


def list_normalization(l, range_size=1):
    """
    Normalization of a list on the 0:r range.
    """
    _max = max(abs(val) if val is not None else None for val in l)
    return [float(val)/_max * range_size if val is not None else 0 for val in l]


def smooth_kaiser(l, window_len=11, beta=5):
    """
    Smoothing operation using a Kaiser window convolution, applied on a list.
    """

    # ensure window_len is maximum half the list size
    if window_len > len(l) / 2:
        window_len = len(l) / 2

    # extending the data at beginning and at the end
    # to apply the window at the borders
    s = numpy.r_[l[window_len-1:0:-1], l, l[-1:-window_len:-1]]
    w = numpy.kaiser(window_len, beta)
    y = numpy.convolve(w / w.sum(), s, mode='valid')

    # Ensure to remove the extending datas at beginning and at the end
    extent = int(window_len/2)
    if window_len % 2 == 0:
        return y[extent:len(y)-extent+1]
    else:
        return y[extent:len(y)-extent]


