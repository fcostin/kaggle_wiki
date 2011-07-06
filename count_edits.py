import csv
import numpy

def main():
    input_tsv_file = 'data/training.tsv'
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
                print 'parse %d' % i
    n = len(count)
    x = numpy.zeros((2, n), dtype = numpy.uint64)
    for i, (u, c) in enumerate(count.iteritems()):
        x[0, i] = u
        x[1, i] = c
        if i % p == 0:
            print 'stash %d' % i
    del count
    numpy.save('usr_edits.npy', x)

if __name__ == '__main__':
    main()
