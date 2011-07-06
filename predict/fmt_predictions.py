import pickle
import numpy
import csv

def main():
    usr_total_edits = numpy.load(open('usr_edits.npy'))
    usr_to_index = pickle.load(open('usr_to_index_map.pickle', 'rb'))
    n_usrs = len(usr_to_index)
    pred_in = csv.reader(open('predictions.csv', 'r'))
    predicted_counts = []
    for i, row in enumerate(pred_in):
        if i == 0:
            continue # skip header
        count = float(row[-1])
        count = numpy.exp(count) - 1.0
        if count < 0.0:
            raise ValueError('lolwut rf?? %s' % count)
        predicted_counts.append(count)

    pred_out = csv.writer(open('fmt_predictions.csv', 'w'), delimiter = ',')
    header = ['user_id', 'count']
    pred_out.writerow(header)
    for usr_id in usr_total_edits[0, :]:
        count = predicted_counts[usr_to_index[usr_id]]
        pred_out.writerow([usr_id, count])

if __name__ == '__main__':
    main()
