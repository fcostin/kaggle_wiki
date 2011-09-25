import csv
import numpy
import time
import pickle

DAYS_PER_YEAR = 365
YEAR_ZERO = 2001
MAX_T = 52 * 10 # overestimate

TIME_FMT = '%Y-%m-%d %H:%M:%S'
def day_to_week(t):
    return t / 7

def main():
    usr_to_index = pickle.load(open('data/usr_to_index_map.pickle', 'rb'))
    n_usrs = len(usr_to_index)
    x = numpy.zeros((n_usrs, MAX_T + 1), dtype = numpy.uint32)

    input_tsv_file = 'original_data/training.tsv'
    p = 1e5 # spam period

    t_week_max = 0
    with open(input_tsv_file, 'r') as f:
        reader = csv.reader(f, delimiter = '\t')
        for i, line in enumerate(reader):
            if i == 0:
                continue # skip header
            usr = int(line[0])
            date = time.strptime(line[4], TIME_FMT)
            t = (date.tm_yday - 1) + DAYS_PER_YEAR * (date.tm_year - YEAR_ZERO)
            t_week = day_to_week(t)
            t_week_max = max(t_week, t_week_max)
            x[usr_to_index[usr], t_week] += 1
            if i % p == 0:
                print 'parse %d' % i
    # trim x since MAX_T was overestimated
    x_trim = numpy.zeros((n_usrs, t_week_max + 1), dtype = numpy.uint32)
    x_trim[:, :] = x[:, :(t_week_max + 1)]
    del x
    numpy.save('data/usr_edits_per_week.npy', x_trim)

if __name__ == '__main__':
    main()
