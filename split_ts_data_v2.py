import csv
import numpy
import sys

def blocked_counts(data, b):
    """
    b : block size
    """
    m, n = data.shape
    # ensure data length is multiple of block size b
    data = data[:, (n % b):]
    # compute b-week block counts
    a = numpy.add.accumulate(data, axis = 1)
    x = a[:, b - 1::b]
    y = numpy.hstack((numpy.zeros((m, 1), dtype = data.dtype), x[:, :-1]))
    return x - y

def test_blocked_counts(data):
    b = 20 # block size
    bcount = blocked_counts(data, b)
    assert numpy.all(bcount[:, -1] == numpy.add.reduce(data[:, -b:], axis = 1))

def first_edit_time(data):
    return numpy.argmax(data > 0, axis = 1)

def last_edit_time(data):
    return numpy.argmax(numpy.add.accumulate(data, axis = 1), axis = 1)

def make_input_features(data, bcount, y = None):
    first_ed = first_edit_time(data)
    last_ed = last_edit_time(data)
    n = bcount.shape[1]
    header = ['b_%d' % i for i in xrange(n)] + ['first_ed', 'last_ed']
    if y is None:
        features = numpy.hstack((
            bcount,
            first_ed[:, numpy.newaxis],
            last_ed[:, numpy.newaxis],
        ))
    else:
        features = numpy.hstack((
            bcount,
            first_ed[:, numpy.newaxis],
            last_ed[:, numpy.newaxis],
            y[:, numpy.newaxis],
        ))
        header.append('y')
    return features, header

def main():
    data_file_name = sys.argv[1]
    out_training_file_name = sys.argv[2]
    out_test_inputs_file_name = sys.argv[3]

    data = numpy.load(data_file_name)
    b = 20

    bcount = blocked_counts(data, b)
    train_bcount_x = bcount[:, :-1]
    train_bcount_y = bcount[:, -1]
    train_features, train_header = make_input_features(
        data[:, :-b],
        train_bcount_x,
        train_bcount_y,
    )
    test_features, test_header = make_input_features(
        data[:, b:],
        bcount[:, 1:],
    )

    outputs = {
        out_training_file_name : (train_features, train_header),
        out_test_inputs_file_name : (test_features, test_header),
    }
    for out_file, (features, header) in outputs.iteritems():
        with open(out_file, 'w') as f:
            print 'Writing shape %s features to "%s"' % (features.shape, out_file)
            writer = csv.writer(f, delimiter = ',')
            writer.writerow(header)
            for row in features:
                writer.writerow(row)

if __name__ == '__main__':
    main()
