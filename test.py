import csv
from numpy import random
import pickle

def take_random_sample(file_name, prob):
    reader = csv.reader(
        open(file_name, 'r'),
        delimiter = '\t',
    )
    p = 0.01
    skip = random.geometric(p)
    lines = []
    spam_period = 10000
    for line in reader:
        skip -= 1
        if skip > 1:
            continue
        lines.append(line)
        if len(lines) % spam_period == 0:
            print len(lines)
        skip = random.geometric(p)
    pickle.dump(lines, open('training_sample.pickle', 'w'))

def main():
    take_random_sample('data/training.tsv', 0.01)

if __name__ == '__main__':
    main()
