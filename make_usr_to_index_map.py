"""
purpose : define an indexing scheme for all users in data set

here users are sorted by increasing total number of edits,
but this was just convenient during development & is
not necessary.
"""


import csv
import numpy
import pickle
import sys

def parse_total_counts(input_tsv_file):
    """
    returns array x of shape (2, n_usrs)
    where x[0, i] is usr_id of i-th usr
    & x[1, i] is total number of edits
    of i-th usr.
    """

    # parse tsv file, accumulating edit counts
    p = 1e5
    count = {}
    with open(input_tsv_file, 'r') as f:
        reader = csv.reader(f, delimiter = '\t')
        for i, line in enumerate(reader):
            if i == 0:
                continue # skip header
            user = int(line[0])
            count[user] = count.get(user, 0) + 1
            if i % p == 0:
                print 'parsing row %d' % i
    n = len(count)
    x = numpy.zeros((2, n), dtype = numpy.uint64)
    for i, (u, c) in enumerate(count.iteritems()):
        x[0, i] = u
        x[1, i] = c
    return x

def main():
    if len(sys.argv) != 3:
        print 'usage: training.tsv output.pickle'
        sys.exit(1)
    in_file_name = sys.argv[1]
    out_file_name = sys.argv[2]

    # parse pairs of (usr_id, total_edit_count)
    x = parse_total_counts(in_file_name)
    # sort by increasing total edit count
    order = numpy.argsort(x[1, :])
    sorted_usr_ids = x[0, order]
    # define mapping from usr_id -> array index
    usr_to_index_map = {}
    for i, usr_id in enumerate(sorted_usr_ids):
        usr_to_index_map[usr_id] = i
    with open(out_file_name, 'wb') as f:
        pickle.dump(usr_to_index_map, f)

if __name__ == '__main__':
    main()
