import numpy
import csv

PREDICTION_WINDOW = 20 # weeks, aka 5 months

MIN_DEPTH = 0
MAX_DEPTH = 8

def shift_data_set(z, t):
    t = int(t)
    assert t >= 0
    if t == 0:
        return numpy.array(z)
    else:
        return numpy.array(z[:, :-t])

def split_data_set(z):
    y = numpy.add.reduce(z[:, -PREDICTION_WINDOW:], axis = 1)
    x = z[:, :-PREDICTION_WINDOW]
    return (x, y)

def make_features(x, min_depth, max_depth):
    print 'making features...'
    max_window_size = 2 ** max_depth
    x = x[:, -max_window_size:]
    names = []
    features = []
    for i in xrange(min_depth, max_depth + 1):
        window_size = 2 ** i
        for j in xrange(0, max_window_size, window_size):
            names.append('X_%d_%d' % (i, j))
            window_mean = numpy.mean(x[:, j:(j + window_size)], axis = 1)
            features.append(window_mean)
    print '\tok'
    return names, features

def make_data_set(z):
    x, y = split_data_set(z)
    feature_names, features = make_features(x, MIN_DEPTH, MAX_DEPTH)
    fx = numpy.asarray(features).T
    return feature_names, fx, y

def write_csv(header, rows, file_name):
    print 'writing csv to "%s"...' % file_name
    with open(file_name, 'w') as f:
        writer = csv.writer(f, delimiter = ',')
        writer.writerow(header)
        writer.writerows(rows)
    print '\tok'

def make_production_input_data_set(z):
    x = z # no period is used for output, this is unknown!
    feature_names, features = make_features(x, MIN_DEPTH, MAX_DEPTH)
    fx = numpy.asarray(features).T
    return feature_names, fx

def main():
    print 'loading usr edits per week...'
    z = numpy.load('../usr_edits_per_week.npy')
    print 'ok'

    print '--------------------------'
    print 'feature generation params:'
    print '\tmin depth: %d' % MIN_DEPTH
    print '\tmax depth: %d' % MAX_DEPTH
    print '--------------------------'

    shifts = (0, PREDICTION_WINDOW, 2 * PREDICTION_WINDOW)
    for shift in shifts:
        print 'shifting data set by shift = %d' % shift
        x_names, x, y = make_data_set(shift_data_set(z, shift))
        write_csv(
            header = list(x_names) + ['Y'],
            rows = numpy.hstack((x, y[:, numpy.newaxis])),
            file_name = 'data_set_shift_%d.csv' % shift,
        )
    # special case for production inputs
    # (since this doesnt have an output column)
    x_names, x = make_production_input_data_set(z)
    write_csv(
        header = list(x_names),
        rows = x,
        file_name = 'data_set_production_inputs.csv',
    )

if __name__ == '__main__':
    main()
