/*------------------------------------------------------------------------------
© A J S Hamilton 2001
------------------------------------------------------------------------------*/
#include <stdio.h>
#include <stdlib.h>
#include "manglefn.h"

/*------------------------------------------------------------------------------
  Minimum and maximum values of cm = 1-cosl(th) between polygon
  and a unit vector rp.

  This is a c interface to fortran subroutine gcmlim.

   Input: poly is a polygon.
	  *tol = angle within which to merge multiple intersections.
	  rp = unit vector.
  Output: minimum and maximum values of cm = 1-cosl(th).
  Return value:  0 if ok;
		-1 if failed to allocate memory.
*/
int gcmlim(polygon *poly, _Float128 *tol, vec rp, _Float128 *cmmin, _Float128 *cmmax)
{
    /* work arrays */
    int *iord;
    _Float128 *phi;

    /* allocate memory for work arrays */
    iord = (int *) malloc(sizeof(int) * poly->np * 2);
    if (!iord) {
	fprintf(stderr, "gcmlim: failed to allocate memory for %d ints\n", poly->np * 2);
	return(-1);
    }
    phi = (_Float128 *) malloc(sizeof(_Float128) * poly->np * 2);
    if (!phi) {
	fprintf(stderr, "gcmlim: failed to allocate memory for %d _Float128s\n", poly->np * 2);
	return(-1);
    }

    /* fortran routine */
    gcmlim_(poly->rp, poly->cm, &poly->np, rp, cmmin, cmmax, tol, phi, iord);

    /* free work arrays */
    free(iord);
    free(phi);

    return(0);
}
