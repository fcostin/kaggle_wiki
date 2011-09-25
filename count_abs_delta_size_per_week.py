"""
purpose : creates table of weekly net |delta| values per user

table is saved as numpy array, binary .npy format
"""

import csv
import numpy
import time
import pickle
import sys

DAYS_PER_YEAR = 365
YEAR_ZERO = 2001
MAX_T = 52 * 10 # overestimate

TIME_FMT = '%Y-%m-%d %H:%M:%S'
def day_to_week(t):
    return t / 7

def main():
    if len(sys.argv) != 4:
        print 'usage: training.tsv usr_to_index_map.pickle output.npy'
        sys.exit(1)
    input_tsv_file_name = sys.argv[1]
    usr_to_index_file_name = sys.argv[2]
    output_file_name = sys.argv[3]

    usr_to_index = pickle.load(open(usr_to_index_file_name, 'rb'))
    n_usrs = len(usr_to_index)
    x = numpy.zeros((n_usrs, MAX_T + 1), dtype = numpy.uint32)

    p = 1e5 # spam period

    t_week_max = 0
    with open(input_tsv_file_name, 'r') as f:
        reader = csv.reader(f, delimiter = '\t')
        for i, line in enumerate(reader):
            if i == 0:
                continue # skip header
            usr = int(line[0])
            date = time.strptime(line[4], TIME_FMT)
            t = (date.tm_yday - 1) + DAYS_PER_YEAR * (date.tm_year - YEAR_ZERO)
            t_week = day_to_week(t)
            t_week_max = max(t_week, t_week_max)
            delta = abs(int(line[-2]))
            x[usr_to_index[usr], t_week] += delta
            if i % p == 0:
                print 'parse %d' % i
    # trim x since MAX_T was overestimated
    x_trim = numpy.zeros((n_usrs, t_week_max + 1), dtype = numpy.uint32)
    x_trim[:, :] = x[:, :(t_week_max + 1)]
    del x
    numpy.save(output_file_name, x_trim)

if __name__ == '__main__':
    main()
