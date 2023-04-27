/*------------------------------------------------------------------------------
© A J S Hamilton 2001
------------------------------------------------------------------------------*/
#ifndef POLYGON_H
#define POLYGON_H

typedef _Float128 vec[3];

typedef struct {		/* polygon structure */
  int np;			/* number of caps of polygon */
  int npmax;			/* dimension of allocated rp and cm arrays */
  vec *rp;			/* pointer to array rp[np][3] of axis coords */
  _Float128 *cm;			/* pointer to array cm[np] of 1 - cosl(theta) */
  long long id;			/* id number of polygon */
  int pixel;                    /* pixel that polygon is in */
  _Float128 weight;		/* weight of polygon */
} polygon;

#endif	/* POLYGON_H */
