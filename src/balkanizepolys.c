/*------------------------------------------------------------------------------
� A J S Hamilton 2001
------------------------------------------------------------------------------*/
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "manglefn.h"

/*------------------------------------------------------------------------------
  Balkanize overlapping polygons into many disjoint connected polygons.

   Input: npoly = number of polygons.
	  poly = array of pointers to polygons.
	  npolys = maximum number of output polygons.
	  mtol = tolerance angle for multiple intersections.
	  fmt = pointer to format structure.
	  axtol, btol, thtol, ytol = tolerance angles (see documentation).
  Output: polys = array of pointers to polygons.
  Return value: number of disjoint connected polygons,
		or -1 if error occurred.
*/
int balkanize(int npoly, polygon *poly[/*npoly*/], int npolys, polygon *polys[/*npolys*/], long double mtol, format *fmt, long double axtol, long double btol, long double thtol, long double ytol)
{
/* part_poly should lasso one-boundary polygons only if they have too many caps */
#define ALL_ONEBOUNDARY		1
/* how part_poly should tighten lasso */
#define ADJUST_LASSO		1
/* part_poly should force polygon to be split even if no part can be lassoed */
#define	FORCE_SPLIT		1
/* partition_poly should overwrite all original polygons */
#define OVERWRITE_ORIGINAL	2
#define WARNMAX			8
    char *snapped_polys = 0x0;
    int discard, dm, dn, dnp, failed, i, ier, inull, isnap, ip, iprune, j, k, m, n, nadj, np, selfsnap;
    int *start;
    int *total;
    int begin, end, p, max_pixel;
    long double tol;

    poly_sort(npoly, poly, 'p');

    /* allocate memory for pixel info arrays start and total */ 
    max_pixel=poly[npoly-1]->pixel+1; 
    start = (int *) malloc(sizeof(int) * max_pixel);
    if (!start) {
      fprintf(stderr, "balkanize: failed to allocate memory for %d integers\n", max_pixel);
      return(-1);
    }
    total = (int *) malloc(sizeof(int) * max_pixel);
    if (!total) {
      fprintf(stderr, "balkanize: failed to allocate memory for %d integers\n", max_pixel);
      return(-1);
    }

    /* build lists of starting indices of each pixel and total number of polygons in each pixel*/
    ier=pixel_list(npoly, poly, max_pixel, start, total);
    if (ier == -1) {
      fprintf(stderr, "balkanize: error building pixel index lists\n");
      return(-1);
    }

    /* start by pruning all input polygons */
    np = 0;
    inull = 0;
    for (i = 0; i < npoly; i++) {
        tol = mtol;
	iprune = prune_poly(poly[i], tol);
	/* error */
	if (iprune == -1) {
	    fprintf(stderr, "balkanize: initial prune failed at polygon %d\n", poly[i]->id);
	    return(-1);
	}
	/* zero area polygon */
	if (iprune >= 2) {
	    if (WARNMAX > 0 && inull == 0) msg("warning from balkanize: following polygons have zero area & are being discarded:\n");
	    if (inull < WARNMAX) {
	      msg(" %lld", (fmt->newid == 'o')? poly[i]->id : (long long)i);
	    } else if (inull == WARNMAX) {
		msg(" ... more\n");
	    }
	    inull++;
	} else {
	    np++;
	}
    }
    if (WARNMAX > 0 && inull > 0 && inull <= WARNMAX) msg("\n");
    if (inull > 0) {
	msg("balkanize: %d polygons with zero area are being discarded;\n", inull);
    }

    /* number of polygons */
    msg("balkanizing %d polygons ...\n", np);

    /* nullify all output polygons */
    for (i = 0; i < npolys; i++) {
	polys[i] = 0x0;
    }

    /*
      m = starting index of current set of fragments of i'th polygon
      dm = number of current set of fragments of i'th polygon
      n = starting index of new subset of fragments of i'th polygon
      dn = number of new subset of fragments of i'th polygon
    */
    
    msg("balkanize stage 1 (fragment into non-overlapping polygons):\n");
    n = 0;
    dnp = 0;
    ip = 0;
    /* go through each pixel and fragment each polygon against the other polygons in its pixel */
    for(p=0;p<max_pixel;p++){
      
      begin=start[p];
      end=start[p]+total[p];

      /* too many polygons */
      if (n >= npolys) break;

      /* fragment each polygon in turn */

      for (i = begin; i < end; i++) {
	/* skip null polygons */
	if (poly[i]->np > 0 && poly[i]->cm[0] == 0.) continue;
	/* update indices */
	
	m = n;
	dm = 1;
        n = m + dm;
        /* make sure output polygon has enough room */
	
	ier = room_poly(&polys[m], poly[i]->np, DNP, 0);
	if (ier == -1) {
	  fprintf(stderr, "balkanize: failed to allocate memory for polygon of %d caps\n", poly[i]->np + DNP);
	  return(-1);
	}
	
	
        /* copy polygon i into output polygon */
	copy_poly(poly[i], polys[m]);
	
	/* fragment successively against other polygons */
	for (j = begin; j < end; j++) {
	
	  /* skip self, or null polygons */
	  if (j == i || (poly[j]->np > 0 && poly[j]->cm[0] == 0.)) continue;
	  /* keep only one copy of the intersection of i & j */
	  /* intersection inherits weight of polygon being fragmented,
	     so keeping later polygon ensures intersection inherits
	     weight of later polygon */
	  if (i < j) {
	    discard = 1;
	  } else {
	    discard = 0;
	  }
	
	  /* fragment each part of i'th polygon */
	  for (k = m; k < m + dm; k++) {
	 	    /* skip null polygons */
	    if (!polys[k] || (polys[k]->np > 0 && polys[k]->cm[0] == 0.)) continue;
	    /* fragment */
	    tol = mtol;
	    dn = fragment_poly(&polys[k], poly[j], discard, npolys - n, &polys[n], tol, bmethod);
 
	    /* error */
	    if (dn == -1) {
	      fprintf(stderr, "balkanize: UHOH at polygon %lld; continuing ...\n", (fmt->newid == 'o')? polys[i]->id : (long long)ip);
	      continue;
	      /* return(-1); */
	    }

	    /* increment index of next subset of fragments */
	    n += dn;
	    /* increment polygon count */
	    np += dn;
	    dnp += dn;
	    if (!polys[k]) {
	      np--;
	      dnp--;
	    }

	    /* check whether exceeded maximum number of polygons */
	    //printf("(1) n = %d\n", n);
	    if (n > npolys) {
	      fprintf(stderr, "(1) balkanize: total number of polygons (= %d) exceeded maximum %d\n", npoly + n, npoly + npolys);
	      fprintf(stderr, "if you need more space, enlarge NPOLYSMAX in defines.h, and recompile\n");
              fprintf(stderr, "currently, dn = %d, np = %d, dnp = %d, poly[%d]->id = %lld, poly[%d]->pixel = %d\n", dn, np, dnp, i, poly[i]->id, i, poly[i]->pixel);
	      n = npolys;
#ifdef	CARRY_ON_REGARDLESS
	      break;
#else
	      return(-1);
#endif
	    }
	  }

	  /* copy down non-null polygons */
	  dm = 0;
	  for (k = m; k < n; k++) {
	    if (polys[k]) {
	      polys[m + dm] = polys[k];
	      dm++;
	    }
	  }
	
	  /* nullify but don't free, because freeing polys[k] will free polys[m + dm] */
	  for (k = m + dm; k < n; k++) {
	    polys[k] = 0x0;
	  }
	  n = m + dm;
	  if (dm == 0) break;
	}
	/* too many polygons */
	if (n >= npolys) break;
	ip++;
      }
      
    }

    free(start);
    free(total);

    msg("added %d polygons to make %d\n", dnp, np);
    
    // partition disconnected polygons into connected parts  
    msg("balkanize stage 2 (partition disconnected polygons into connected parts):\n");
    m = n;
    dnp = 0;
    ip = 0;
    failed = 0;
    for (i = 0; i < m; i++) {
	// skip null polygons 
	if (!polys[i] || (polys[i]->np > 0 && polys[i]->cm[0] == 0.)) continue;
	// partition disconnected polygons
	tol = mtol;
	ier = partition_poly(&polys[i], npolys - n, &polys[n], tol, ALL_ONEBOUNDARY, ADJUST_LASSO, FORCE_SPLIT, OVERWRITE_ORIGINAL, &dn);
	// error
	if (ier == -1) {
	  fprintf(stderr, "balkanize: UHOH at polygon %lld; continuing ...\n", (fmt->newid == 'o')? polys[i]->id : (long long)ip);
	    continue;
	    // return(-1);
	// failed to partition polygon into desired number of parts
	} else if (ier == 1) {
	  fprintf(stderr, "balkanize: failed to partition polygon %lld fully; partitioned it into %d parts\n", (fmt->newid == 'o')? polys[i]->id : (long long)ip, dn + 1);
	    failed++;
	}
	// increment index of next subset of fragments 
	n += dn;
	// increment polygon count
	np += dn;
	dnp += dn;
	// check whether exceeded maximum number of polygons
	//printf("(2) n = %d\n", n);
	if (n > npolys) {
	    fprintf(stderr, "(2) balkanize: total number of polygons (= %d) exceeded maximum %d\n", n + npoly, npoly + npolys);
	    fprintf(stderr, "if you need more space, enlarge NPOLYSMAX in defines.h, and recompile\n");
	    n = npolys;
#ifdef	CARRY_ON_REGARDLESS
	    break;
#else
	    return(-1);
#endif
	}
	ip++;
    }

    msg("added %d polygons to make %d\n", dnp, np);

    if (failed > 0) {
	msg("balkanize: failed to split %d polygons into desired number of connected parts\n", failed);
	msg(".............................................................................\n");
	msg("Failure to split polygon probably means:\n");
	msg("either (1) you forgot to run snap on all your input polygon files;\n");
	msg("    or (2) the polygon is too small for the numerics to cope with;\n");
	msg("    or (3) you have a weird-shaped polygon.\n");
	msg("You may ignore this warning message if the weights of polygons in the input\n");
	msg("polygon file(s) are already correct, and you do not want to reweight them.\n");
	msg("Similarly, you may ignore this warning message if you do want to reweight the\n");
	msg("polygons, but the weights of the different parts of each unsplit polygon are\n");
	msg("the same.  If you want to reweight the different parts of an unsplit polygon\n");
	msg("with different weights, then you will need to split that polygon by hand.\n");
	msg("Whatever the case, the output file of balkanized polygons constitutes\n");
	msg("a valid mask of non-overlapping polygons, which is safe to use.\n");
	msg(".............................................................................\n");
    }

    /* prune */
    j = 0;
    inull = 0;
    for (i = 0; i < n; i++) {
        tol = mtol;
	iprune = prune_poly(polys[i], tol);
	if (iprune == -1) {
	  fprintf(stderr, "balkanize: failed to prune polygon %lld; continuing ...\n", (fmt->newid == 'o')? polys[i]->id : (long long)j);
	    /* return(-1); */
	}
	if (iprune >= 2) {
	    free_poly(polys[i]);
	    polys[i] = 0x0;
	    inull++;
	} else {
	    polys[j] = polys[i];
	    j++;
	}
    }
    if (inull > 0) msg("balkanize: %d balkanized polygons have zero area, and are being discarded\n", inull);
    n = j;

    /*    
    // allocate snapped_polys array
    snapped_polys = (char *) malloc(sizeof(char) * n);
    if (!snapped_polys) {
	fprintf(stderr, "balkanize: failed to allocate memory for %d characters\n", n);
	return(-1);
    }

    //snap edges of each polygon 
    selfsnap = 1;
    nadj = snap_polys(fmt, n, polys, selfsnap, axtol, btol, thtol, ytol, mtol, WARNMAX, snapped_polys);
    if(nadj==-1){
      msg("balkanize: error snapping balkanized polygons\n");
      return(-1);
    }

    // number of polygons whose edges were snapped
    isnap = 0;
    for (i = 0; i < n; i++) if (snapped_polys[i]) isnap++;
    if (isnap > 0) msg("balkanize: edges of %d balkanized polygons were snapped\n", isnap);

    // prune snapped polygons 
    j = 0;
    inull = 0;
    for (i = 0; i < n; i++) {
	if (snapped_polys[i]) {
	    iprune = prune_poly(polys[i], mtol);
	    if (iprune == -1) {
		fprintf(stderr, "balkanize: failed to prune polygon %lld; continuing ...\n", (fmt->newid == 'o')? polys[i]->id : (long long)j);
		// return(-1); 
	    }
	    if (iprune >= 2) {
		free_poly(polys[i]);
		polys[i] = 0x0;
		inull++;
	    } else {
		polys[j] = polys[i];
		j++;
	    }
	} else {
	    polys[j] = polys[i];
	    j++;
	}
    }
    
    if (inull > 0) msg("balkanize: %d snapped polygons have zero area, and are being discarded\n", inull);
    n = j;

// free snapped_polys array 
    free(snapped_polys);
    */

    if(n!=-1){
      /* sort polygons by pixel number */
      poly_sort(n, polys,'p');
      msg("balkanize: balkans contain %d polygons\n", n); 
    }
 
    /* assign new polygon id numbers in place of inherited ids */
    if (fmt->newid == 'n') {
	for (i = 0; i < n; i++) {
	  polys[i]->id = (long long)i;
	}
    }

    if (fmt->newid == 'p') {
      for (i = 0; i < n; i++) {
	polys[i]->id = (long long)polys[i]->pixel;
      }
    }

   
    return(n);
}
