import numpy
import csv

def main():
    x = numpy.load('usr_edits_per_5month.npy')
    n_usrs, n_months = x.shape

    with open('usr_edits_per_5month.csv', 'w') as f:
        writer = csv.writer(f)
        header = ['month_%d' % i for i in xrange(n_months)]
        writer.writerow(header)

        for row in x:
            writer.writerow(row)

if __name__ == '__main__':
    main()
