import mesh.reconstruction_f as reconstruction_f
import mesh.patch as patch
import mesh.array_indexer as ai

def fluxes(my_data, rp, dt):
    """
    Construct the fluxes through the interfaces for the linear advection
    equation:

      a  + u a  + v a  = 0
       t      x      y

    We use a second-order (piecewise linear) Godunov method to construct
    the interface states, using Runge-Kutta integration.  These are
    one-dimensional predictions to the interface, relying on the
    coupling in transverse directions through the intermediate stages
    of the Runge-Kutta integrator.

    In the pure advection case, there is no Riemann problem we need to
    solve -- we just simply do upwinding.  So there is only one 'state'
    at each interface, and the zone the information comes from depends
    on the sign of the velocity.

    Our convection is that the fluxes are going to be defined on the
    left edge of the computational zones


     |             |             |             |
     |             |             |             |
    -+------+------+------+------+------+------+--
     |     i-1     |      i      |     i+1     |

              a_l,i  a_r,i   a_l,i+1


    a_r,i and a_l,i+1 are computed using the information in
    zone i,j.

    Parameters
    ----------
    my_data : CellCenterData2d object
        The data object containing the grid and advective scalar that
        we are advecting.
    rp : RuntimeParameters object
        The runtime parameters for the simulation
    dt : float
        The timestep we are advancing through.
    scalar_name : str
        The name of the variable contained in my_data that we are
        advecting

    Returns
    -------
    out : ndarray, ndarray
        The fluxes on the x- and y-interfaces

    """

    myg = my_data.grid

    a = my_data.get_var("density")

    # get the advection velocities
    u = rp.get_param("advection.u")
    v = rp.get_param("advection.v")

    qx = myg.qx
    qy = myg.qy

    #--------------------------------------------------------------------------
    # monotonized central differences
    #--------------------------------------------------------------------------

    limiter = rp.get_param("advection.limiter")

    if limiter < 10:
        if limiter == 0:
            limit_func = reconstruction_f.nolimit
        elif limiter == 1:
            limit_func = reconstruction_f.limit2
        else:
            limit_func = reconstruction_f.limit4

        _lda = limit_func(1, a, qx, qy, myg.ng)
        ldelta_ax = ai.ArrayIndexer(d=_lda, grid=myg)

        _lda = limit_func(2, a, qx, qy, myg.ng)
        ldelta_ay = ai.ArrayIndexer(d=_lda, grid=myg)

    else:
        _ldax, _lday = reconstruction_f.multid_limit(a, qx, qy, myg.ng)
        ldelta_ax = ai.ArrayIndexer(d=_ldax, grid=myg)
        ldelta_ay = ai.ArrayIndexer(d=_lday, grid=myg)

    a_x = myg.scratch_array()

    # upwind
    if u < 0:
        # a_x[i,j] = a[i,j] - 0.5*(1.0 + cx)*ldelta_a[i,j]
        a_x.v(buf=1)[:,:] = a.v(buf=1) - 0.5*ldelta_ax.v(buf=1)
    else:
        # a_x[i,j] = a[i-1,j] + 0.5*(1.0 - cx)*ldelta_a[i-1,j]
        a_x.v(buf=1)[:,:] = a.ip(-1, buf=1) + 0.5*ldelta_ax.ip(-1, buf=1)


    # y-direction
    a_y = myg.scratch_array()

    # upwind
    if v < 0:
        # a_y[i,j] = a[i,j] - 0.5*(1.0 + cy)*ldelta_a[i,j]
        a_y.v(buf=1)[:,:] = a.v(buf=1) - 0.5*ldelta_ay.v(buf=1)
    else:
        # a_y[i,j] = a[i,j-1] + 0.5*(1.0 - cy)*ldelta_a[i,j-1]
        a_y.v(buf=1)[:,:] = a.jp(-1, buf=1) + 0.5*ldelta_ay.jp(-1, buf=1)


    F_x = u*a_x
    F_y = v*a_y

    return F_x, F_y
