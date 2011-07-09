import csv

def main():
    rows = []
    header = None
    with open('predictions.csv', 'r') as f_in:
        reader = csv.reader(f_in, delimiter = ',')
        for i, row in enumerate(reader):
            if i == 0:
                header = row
            else:
                rows.append((int(row[0]), float(row[1])))
    rows = sorted(rows)
    with open('sorted_predictions.csv', 'w') as f_out:
        writer = csv.writer(f_out, delimiter = ',')
        writer.writerow(header)
        writer.writerows(rows)

if __name__ == '__main__':
    main()

