import pylab
import numpy
from util import runparams

def dovis(myData, n):

    pylab.clf()

    dens = myData.getVarPtr("density")

    myg = myData.grid

    pylab.imshow(numpy.transpose(dens[myg.ilo:myg.ihi+1,myg.jlo:myg.jhi+1]), 
                 interpolation="nearest", origin="lower",
                 extent=[myg.xmin, myg.xmax, myg.ymin, myg.ymax])

    pylab.xlabel("x")
    pylab.ylabel("y")
    pylab.title("density")

    pylab.colorbar()

    pylab.draw()

    store = runparams.getParam("vis.store_images")

    if (store == 1):
        basename = runparams.getParam("io.basename")
        pylab.savefig(basename + "%4.4d" % (n) + ".png")
