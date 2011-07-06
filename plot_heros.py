import numpy
import pylab

def main():
    x = numpy.load('usr_edits_per_month.npy')
    n_usrs, n_months = x.shape

    n_across = 2
    n_down = 4
    pylab.figure(figsize = (16, 10), dpi = 200)
    pylab.suptitle('HERO EDITOR HALL OF FAME')
    for i in xrange(n_across):
        for j in xrange(n_down):
            k = i * n_down + j
            pylab.subplot(n_across, n_down, k + 1)
            pylab.title('heroic editor # %d' % (k + 1))
            pylab.plot(numpy.arange(n_months), numpy.log(1.0 + x[-(1 + k), :]), '+-')
            pylab.xlabel('month')
            pylab.ylabel('log(1 + edits)')
    pylab.savefig('hall_of_fame.png', dpi = 200)

if __name__ == '__main__':
    main()
