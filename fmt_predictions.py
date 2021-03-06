import pickle
import numpy
import csv
import sys

def main():
    if len(sys.argv) != 4:
        print 'usage: usr_to_index_map.pickle raw_predictions.csv predictions.csv'
        sys.exit(1)
    usr_to_index = pickle.load(open(sys.argv[1], 'rb'))
    n_usrs = len(usr_to_index)
    pred_in = csv.reader(open(sys.argv[2], 'r'))
    predicted_counts = []
    for i, row in enumerate(pred_in):
        if i == 0:
            continue # skip header
        count = float(row[-1])
        assert numpy.isfinite(count) and count >= 0.0
        predicted_counts.append(count)
    
    print 'saving correctly formatted predictions to "%s"' % sys.argv[2]
    pred_out = csv.writer(open(sys.argv[3], 'w'), delimiter = ',')
    header = ['user_id', 'count']
    pred_out.writerow(header)
    sorted_usr_ids = sorted(map(int, usr_to_index.keys()))
    for usr_id in sorted_usr_ids:
        count = predicted_counts[usr_to_index[usr_id]]
        pred_out.writerow([usr_id, count])

if __name__ == '__main__':
    main()
