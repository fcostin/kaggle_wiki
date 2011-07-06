import pickle
import pylab
import numpy
import time

def main():
    print 'depickling'
    rows = pickle.load(open('training_sample.pickle', 'r'))
    print 'okok'

    usr_count = {}
    art_count = {}
    for row in rows:
        usr = row[0]
        art = row[1]
        usr_count[usr] = usr_count.get(usr, 0) + 1
        art_count[art] = art_count.get(art, 0) + 1
    
    usr_summ = {}
    for _, count in usr_count.iteritems():
        usr_summ[count] = usr_summ.get(count, 0) + 1


    art_summ = {}
    for _, count in art_count.iteritems():
        art_summ[count] = art_summ.get(count, 0) + 1
    
    print 'usr_summ'
    for n_edits in sorted(usr_summ):
        print '%d : %d' % (n_edits, usr_summ[n_edits])

    print 'art_summ'
    for n_edits in sorted(art_summ):
        print '%d : %d' % (n_edits, art_summ[n_edits])


    pylab.figure()
    pylab.subplot(2, 2, 1)
    pylab.plot(sorted(usr_count.values()))
    pylab.title('sorted usr count values')
    pylab.subplot(2, 2, 2)
    pylab.plot(numpy.log(numpy.asarray(sorted(usr_count.values())) + 1.0))
    pylab.title('sorted usr count values; x -> log(1 + x)')
    pylab.subplot(2, 2, 3)
    pylab.plot(sorted(art_count.values()))
    pylab.title('sorted art count values')
    pylab.subplot(2, 2, 4)
    pylab.plot(numpy.log(numpy.asarray(sorted(art_count.values())) + 1.0))
    pylab.title('sorted art count values; x -> log(1 + x)')
    pylab.subplot(2, 2, 3)


    n_top_eds = 30
    top_eds = sorted(usr_count.items(), key = lambda (k, v) : v, reverse = True)[:n_top_eds]
    print 'top eds:'
    print str(top_eds)
    print ''
    time_fmt = '%Y-%m-%d %H:%M:%S'
    for i, (ed_id, ed_count) in enumerate(top_eds):
        pylab.figure()
        pylab.title('top ed number %d' % i)

        # time string -> seconds since 1 1 1
        parse_time = lambda s : time.mktime(time.strptime(s, time_fmt))
        
        print 'ed_id : "%s"' % ed_id
        times = []
        for row in rows:
            usr = row[0]
            if usr == ed_id:
                t = parse_time(row[4])
                times.append(t)
        times = numpy.asarray(times)
        lo = times.min()
        times -= lo
        times.sort()
        pylab.plot(times, '+-')

    pylab.show()

if __name__ == '__main__':
    main()
