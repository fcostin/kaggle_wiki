import csv
import numpy
import time
import pickle

YEAR_ZERO = 2001
YEAR_MAX = 2010
MONTH_MAX = 7 # august
MONTHS_PER_YEAR = 12
MAX_T = (YEAR_MAX - YEAR_ZERO) * MONTHS_PER_YEAR + MONTH_MAX

TIME_FMT = '%Y-%m-%d %H:%M:%S'

def main():
    usr_to_index = pickle.load(open('usr_to_index_map.pickle', 'rb'))
    n_usrs = len(usr_to_index)
    x = numpy.zeros((n_usrs, MAX_T + 1), dtype = numpy.uint32)

    input_tsv_file = 'data/training.tsv'
    p = 1e5 # spam period

    with open(input_tsv_file, 'r') as f:
        reader = csv.reader(f, delimiter = '\t')
        for i, line in enumerate(reader):
            if i == 0:
                continue # skip header
            usr = int(line[0])
            date = time.strptime(line[4], TIME_FMT)
            # subtract 1 so months go from 0 to 11 inclusive
            t = MONTHS_PER_YEAR * (date.tm_year - YEAR_ZERO) + (date.tm_mon - 1)
            x[usr_to_index[usr], t] += 1
            if i % p == 0:
                print 'parse %d' % i
    numpy.save('usr_edits_per_month.npy', x)

if __name__ == '__main__':
    main()
