import csv
import numpy
import sys

SAMPLING_INTERVAL_WEEK = 451 # XXX this is approximately around 1st Sept 2009
MAX_RELEVANT_BLOCKS = 14 # XXX arbitrary

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

def mean_edits_since_first(data, first_edit_index):
    acc = numpy.add.accumulate(data, axis = 1)
    n_edits_since_first = []
    for i in xrange(data.shape[0]):
        # add 1 as to include the first edit too
        n_edits_since_first.append(
            acc[i, -1] - acc[i, first_edit_index[i]] + 1
        )
    n_edits_since_first = numpy.asarray(n_edits_since_first)
    now_index = data.shape[1]
    return (1.0 / (now_index - first_edit_index)) * n_edits_since_first

def make_input_features(data, bcount, y = None, t_offset = 0):
    first_ed_index = first_edit_time(data)
    last_ed_index = last_edit_time(data)
    first_ed = first_ed_index + t_offset
    last_ed = last_ed_index + t_offset
    new_user = first_ed > SAMPLING_INTERVAL_WEEK
    edit_rate = mean_edits_since_first(data, first_ed_index)
    
    # hack : ignore blocks from pre-history
    bcount = bcount[:, -MAX_RELEVANT_BLOCKS:]
    n = bcount.shape[1]
    header = (
        ['b_%d' % i for i in xrange(n)] +
        ['first_ed', 'last_ed', 'new_user', 'edit_rate']
    )
    features = [
        bcount,
        first_ed[:, numpy.newaxis],
        last_ed[:, numpy.newaxis],
        new_user[:, numpy.newaxis],
        edit_rate[:, numpy.newaxis],
    ]
    if y is not None:
        features.append(y[:, numpy.newaxis])
        header.append('y')
    features = numpy.hstack(features)
    return features, header

def main():
    if len(sys.argv) != 4:
        print 'usage: data_file_name out_training_file_name out_test_inputs_file_name'
        sys.exit(1)
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
        t_offset = b,
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
