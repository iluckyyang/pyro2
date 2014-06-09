import sys
import mesh.patch as patch
import numpy
from util import msg

def initData(my_data):
    """ initialize the smooth advection problem """

    msg.bold("initializing the smooth advection problem...")

    rp = my_data.rp

    # make sure that we are passed a valid patch object
    if not isinstance(my_data, patch.CellCenterData2d):
        print "ERROR: patch invalid in smooth.py"
        print my_data.__class__
        sys.exit()

    dens = my_data.getVarPtr("density")

    xmin = my_data.grid.xmin
    xmax = my_data.grid.xmax

    ymin = my_data.grid.ymin
    ymax = my_data.grid.ymax

    xctr = 0.5*(xmin + xmax)
    yctr = 0.5*(ymin + ymax)
    
    i = my_data.grid.ilo
    while i <= my_data.grid.ihi:

        j = my_data.grid.jlo
        while j <= my_data.grid.jhi:

            dens[i,j] = 1.0 + numpy.exp(-60.0*((my_data.grid.x[i]-xctr)**2 + \
                                               (my_data.grid.y[j]-yctr)**2))
                    
            j += 1
        i += 1
    

    
def finalize():
    """ print out any information to the user at the end of the run """
    pass
