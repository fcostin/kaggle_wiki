import pickle
import numpy
import csv

def main():
    usr_to_index = pickle.load(open('usr_to_index_map.pickle', 'r'))
    x = numpy.load('usr_edits_per_5month.npy')

    writer = csv.writer(
        open('predictions.csv', 'w'),
        delimiter = ',',
    )
    header = ['user', 'count']
    writer.writerow(header)
    for usr in usr_to_index:
        count = x[usr_to_index[usr], -1]
        writer.writerow((usr, count))

if __name__ == '__main__':
    main()

