/*------------------------------------------------------------------------------
© A J S Hamilton 2001
------------------------------------------------------------------------------*/
#include "manglefn.h"

/*------------------------------------------------------------------------------
  c interface to fortran subroutines in braktop.s.f
*/
void braktop(_Float128 aa, int *ia, _Float128 a[], int n, int l)
{
    braktop_(&aa, ia, a, &n, &l);
}

void brakbot(_Float128 aa, int *ia, _Float128 a[], int n, int l)
{
    brakbot_(&aa, ia, a, &n, &l);
}

void braktpa(_Float128 aa, int *ia, _Float128 a[], int n, int l)
{
    braktpa_(&aa, ia, a, &n, &l);
}

void brakbta(_Float128 aa, int *ia, _Float128 a[], int n, int l)
{
    brakbta_(&aa, ia, a, &n, &l);
}
