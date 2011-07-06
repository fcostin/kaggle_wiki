import cPickle
import pylab
import numpy
import time

def main():
    print 'depickling'
    rows = cPickle.load(open('training_sample.pickle', 'r'))
    print 'okok'

    time_fmt = '%Y-%m-%d %H:%M:%S'
    parse_time = lambda s : time.mktime(time.strptime(s, time_fmt))

    usr_edits = {}
    art_edits = {}
    namespace_counts = {}
    for i in xrange(6):
        namespace_counts[i] = 0

    print 'building maps'
    for row in rows:
        usr = int(row[0])
        art = int(row[1])
        namespace = int(row[3])
        namespace_counts[namespace] += 1

        t = parse_time(row[4])
        if usr not in usr_edits:
            usr_edits[usr] = []
        usr_edits[usr].append((t, art, namespace))
        if art not in art_edits:
            art_edits[art] = []
        art_edits[art].append((t, usr, namespace))
    print 'okok'
    blob = {
        'usr_edits' : usr_edits,
        'art_edits' : art_edits,
    }
    cPickle.dump(blob, open('blob.pickle', 'wb'))
    return # XXX

    for i in sorted(namespace_counts):
        print 'namespace %d : count %d' % (i, namespace_counts[i])

    print 'sorting'
    # chron order everything
    for usr in usr_edits:
        usr_edits[usr] = sorted(usr_edits[usr])

    for art in art_edits:
        art_edits[art] = sorted(art_edits[art])
    print 'okok'


    print 'plotting some stats'
    rho = []
    nu = []
    for usr in usr_edits:
        adj_arts = list(set([art for (t, art, ns) in usr_edits[usr]]))
        adj_usrs = list(set([usr for (t, usr, ns) in art_edits[art] for art in adj_arts]))

        n_edits = len(usr_edits[usr])
        n_adj_arts = len(adj_arts)
        n_adj_usrs = len(adj_usrs)
        rho.append(float(n_edits) / float(n_adj_arts))
        nu.append(n_adj_usrs)

    nu = numpy.log(1.0 + numpy.asarray(nu))
    rho = numpy.log(1.0 + numpy.asarray(rho))

    pylab.figure()
    pylab.subplot(2, 2, 1)
    pylab.scatter(rho, nu, s = 100, alpha = 0.1)
    pylab.xlabel('log(1 + n_edits / n_adj_arts)')
    pylab.ylabel('log(1 + n_adj_usrs)')
    pylab.subplot(2, 2, 2)
    pylab.title('rho = log(1 + n_edits / |adj_arts|)')
    pylab.hist(rho, 100)
    pylab.subplot(2, 2, 3)
    pylab.title('nu = log(1 + |adj_usrs|)')
    pylab.hist(nu, 100)
    print 'okok'
    pylab.show()

if __name__ == '__main__':
    main()
