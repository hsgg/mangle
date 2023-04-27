/*------------------------------------------------------------------------------
© A J S Hamilton 2003
------------------------------------------------------------------------------*/
#ifndef MANGLEFN_H
#define MANGLEFN_H

#include "defines.h"
#include "format.h"
#include "harmonics.h"
#include "logical.h"
#include "polygon.h"
#include "vertices.h"
#include "polysort.h"

void	advise_fmt(format *);

void	azel_(_Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *);
void	azell_(_Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *);

void	braktop(_Float128, int *, _Float128 [], int, int);
void	brakbot(_Float128, int *, _Float128 [], int, int);
void	braktpa(_Float128, int *, _Float128 [], int, int);
void	brakbta(_Float128, int *, _Float128 [], int, int);
void	braktop_(_Float128 *, int *, _Float128 [], int *, int *);
void	brakbot_(_Float128 *, int *, _Float128 [], int *, int *);
void	braktpa_(_Float128 *, int *, _Float128 [], int *, int *);
void	brakbta_(_Float128 *, int *, _Float128 [], int *, int *);

void	cmminf(polygon *, int *, _Float128 *);

void	vert_to_poly(vertices *, polygon *);
void	edge_to_poly(vertices *, int, int *, polygon *);
void    rect_to_poly(_Float128 [4], polygon *);

#ifdef	GCC
void	rps_to_vert(int nv, vec [nv], vertices *);
#else
void	rps_to_vert(int nv, vec [/*nv*/], vertices *);
#endif
void	rp_to_azel(vec, azel *);
void	azel_to_rp(azel *, vec);
void	azel_to_gc(azel *, azel *, vec, _Float128 *);
void	rp_to_gc(vec, vec, vec, _Float128 *);
void	edge_to_rpcm(azel *, azel *, azel *, vec, _Float128 *);
void	rp_to_rpcm(vec, vec, vec, vec, _Float128 *);
void	circ_to_rpcm(_Float128 [3], vec, _Float128 *);
void	rpcm_to_circ(vec, _Float128 *, _Float128 [3]);
void	az_to_rpcm(_Float128, int, vec, _Float128 *);
void	el_to_rpcm(_Float128, int, vec, _Float128 *);
_Float128	thij(vec, vec);
_Float128	cmij(vec, vec);
int	poly_to_rect(polygon *, _Float128 *, _Float128 *, _Float128 *, _Float128 *);
int	antivert(vertices *, polygon *);

void	copy_format(format *, format *);

void	copy_poly(polygon *, polygon *);
void	copy_polyn(polygon *, int, polygon *);
void	poly_poly(polygon *, polygon *, polygon *);
void	poly_polyn(polygon *, polygon *, int, int, polygon *);
#ifdef	GCC
void	group_poly(polygon *poly, int [poly->np], int, polygon *);
#else
void	group_poly(polygon *poly, int [/*poly->np*/], int, polygon *);
#endif
void    assign_parameters();
void    pix2ang(int, unsigned long, _Float128 *, _Float128 *);
void    ang2pix(int, _Float128, _Float128, unsigned long *);
void    pix2ang_radec(int, unsigned long, _Float128 *, _Float128 *);
void    ang2pix_radec(int, _Float128, _Float128, unsigned long *);
void    csurvey2eq(_Float128, _Float128, _Float128 *, _Float128 *);
void    eq2csurvey(_Float128, _Float128, _Float128 *, _Float128 *);
void    superpix(int, unsigned long, int, unsigned long *);
void    subpix(int, unsigned long, unsigned long *, unsigned long *, unsigned long *, unsigned long *);
void    pix_bound(int, unsigned long, _Float128 *, _Float128 *, _Float128 *, _Float128 *);
_Float128  pix_area(int, unsigned long);
void    pix2xyz(int, unsigned long, _Float128 *, _Float128 *, _Float128 *);
void    area_index(int, _Float128, _Float128, _Float128, _Float128, unsigned long *, unsigned long *, unsigned long *, unsigned long *);
void    area_index_stripe(int, int, unsigned long *, unsigned long *, unsigned long *, unsigned long *);

_Float128	drandom(void);

#ifdef	GCC
int	cmlim_polys(int npoly, polygon *[npoly], _Float128, vec);
int	drangle_polys(int npoly, polygon *[npoly], _Float128, vec, int nth, _Float128 [nth], _Float128 [nth]);
#else
int	cmlim_polys(int npoly, polygon *[/*npoly*/], _Float128, vec);
int	drangle_polys(int npoly, polygon *[/*npoly*/], _Float128, vec, int nth, _Float128 [/*nth*/], _Float128 [/*nth*/]);
#endif

void	cmlimpolys_(_Float128 *, vec);
#ifdef	GCC
void	dranglepolys_(_Float128 *, vec, int *nth, _Float128 [*nth], _Float128 [*nth]);
#else
void	dranglepolys_(_Float128 *, vec, int *nth, _Float128 [/**nth*/], _Float128 [/**nth*/]);
#endif

#ifdef	GCC
void	dump_poly(int npoly, polygon *[npoly]);
#else
void	dump_poly(int, polygon *[/*npoly*/]);
#endif

void	fframe_(int *, _Float128 *, _Float128 *, int *, _Float128 *, _Float128 *);

void	findtop(_Float128 [], int, int [], int);
void	findbot(_Float128 [], int, int [], int);
void	findtpa(_Float128 [], int, int [], int);
void	findbta(_Float128 [], int, int [], int);
void	finitop(int [], int, int [], int);
void	finibot(int [], int, int [], int);
void	finitpa(int [], int, int [], int);
void	finibta(int [], int, int [], int);

void	findtop_(_Float128 [], int *, int [], int *);
void	findbot_(_Float128 [], int *, int [], int *);
void	findtpa_(_Float128 [], int *, int [], int *);
void	findbta_(_Float128 [], int *, int [], int *);
void	finitop_(int [], int *, int [], int *);
void	finibot_(int [], int *, int [], int *);
void	finitpa_(int [], int *, int [], int *);
void	finibta_(int [], int *, int [], int *);

polygon *get_pixel(int,char);
int     get_child_pixels(int, int [], char);
int     get_parent_pixels(int, int [], char);
int     get_res(int,char);

void    healpix_ang2pix_nest(int, _Float128, _Float128, int *);
polygon *get_healpix_poly(int, int);
int     get_nside(int);
void    healpix_verts(int, int, vec, _Float128 []);
void    pix2vec_nest__(int *, int *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *);
_Float128  cmrpirpj(vec, vec);

int	garea(polygon *, _Float128 *, int, _Float128 *);
int	gcmlim(polygon *, _Float128 *, vec, _Float128 *, _Float128 *);
int	gphbv(polygon *, int, int, _Float128 *, _Float128 [2], _Float128 [2]);
int	gphi(polygon *, _Float128 *, vec, _Float128, _Float128 *);
int	gptin(polygon *, vec);
#ifdef	GCC
int	gspher(polygon *, int lmax, _Float128 *, _Float128 *, _Float128 [2], _Float128 [2], harmonic [NW]);
int	gsphera(_Float128, _Float128, _Float128, _Float128, int lmax, _Float128 *, _Float128 [2], _Float128 [2], harmonic [NW]);
int	gsphr(polygon *, int lmax, _Float128 *, harmonic [NW]);
int	gsphra(_Float128, _Float128, _Float128, _Float128, int lmax, harmonic [NW]);
#else
int	gspher(polygon *, int lmax, _Float128 *, _Float128 *, _Float128 [2], _Float128 [2], harmonic [/*NW*/]);
int	gsphera(_Float128, _Float128, _Float128, _Float128, int lmax, _Float128 *, _Float128 [2], _Float128 [2], harmonic [/*NW*/]);
int	gsphr(polygon *, int lmax, _Float128 *, harmonic [/*NW*/]);
int	gsphra(_Float128, _Float128, _Float128, _Float128, int lmax, harmonic [/*NW*/]);
#endif
int	gverts(polygon *, int, _Float128 *, int, int, int *, vec **, _Float128 **, int **, int **, int *, int *, int **);
#ifdef	GCC
int	gvert(polygon *poly, int, _Float128 *, int nvmax, int, int nve, int *, vec [nvmax * nve], _Float128 [nvmax], int [nvmax], int [poly->np], int *, int *, int [nvmax]);
#else
int	gvert(polygon *poly, int, _Float128 *, int nvmax, int, int nve, int *, vec [/*nvmax * nve*/], _Float128 [/*nvmax*/], int [/*nvmax*/], int [/*poly->np*/], int *, int *, int [/*nvmax*/]);
#endif
int	gvlims(polygon *, int, _Float128 *, vec, int *, vec **, vec **, _Float128 **, _Float128 **, _Float128 **, _Float128 **, int **, int **, int *, int *, int **);
#ifdef	GCC
int	gvlim(polygon *poly, int, _Float128 *, vec, int nvmax, int *, vec [nvmax], vec [nvmax], _Float128 [nvmax], _Float128 [nvmax], _Float128 [poly->np], _Float128 [poly->np], int [nvmax], int [poly->np], int *, int *, int [nvmax]);
#else
int	gvlim(polygon *poly, int, _Float128 *, vec, int nvmax, int *, vec [/*nvmax*/], vec [/*nvmax*/], _Float128 [/*nvmax*/], _Float128 [/*nvmax*/], _Float128 [/*poly->np*/], _Float128 [/*poly->np*/], int [/*nvmax*/], int [/*poly->np*/], int *, int *, int [/*nvmax*/]);
#endif
int	gvphi(polygon *, vec, _Float128, vec, _Float128 *, _Float128 *, vec);

void	garea_(_Float128 *, vec [], _Float128 [], int *, _Float128 *, int *, _Float128 *, int *, logical *);
void	gaxisi_(vec, vec, vec);
void	gcmlim_(vec [], _Float128 [], int *, vec, _Float128 *, _Float128 *, _Float128 *, _Float128 *, int *);
void	gphbv_(_Float128 [2], _Float128 [2], vec [], _Float128 [], int *, int *, int *, int *, _Float128 *, _Float128 *, int *);
void	gphi_(_Float128 *, vec [], _Float128 [], int *, vec, _Float128 *, _Float128 *, _Float128 *, int *);
logical	gptin_(vec [], _Float128 [], int *, vec);
void	gspher_(_Float128 *, _Float128 [2], _Float128 [2], harmonic [], int *, int *, int *, vec [], _Float128 [], int *, int *, int *, int *, _Float128 *, _Float128 *, int *, _Float128 *, logical *);
void	gsphera_(_Float128 *, _Float128 [2], _Float128 [2], harmonic [], int *, int *, int *, int *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *, _Float128 *);
void	gvert_(vec [], _Float128 [], int [], int [], int [], int *, int *, int *, int *, int *, int *, vec [], _Float128 [], int *, int *, _Float128 *, _Float128 *, int *, _Float128 *, int *, logical *);

void	gvlim_(vec [], vec [], _Float128 [], _Float128 [], _Float128 [], _Float128 [], int [], int [], int [], int *, int *, int *, int *, vec [], _Float128 [], int *, _Float128 [], int *, _Float128 *, _Float128 *, int *, _Float128 *, int *, logical *);
void	gvphi_(_Float128 *, vec, vec [], _Float128 [], int *, vec, _Float128 *, vec, _Float128 *, _Float128 *, int *);

#ifdef	GCC
int	harmonize_polys(int npoly, polygon *[npoly], _Float128, int lmax, harmonic w[NW]);
#else
int	harmonize_polys(int npoly, polygon *poly[/*npoly*/], _Float128, int lmax, harmonic w[/*NW*/]);
#endif

void	harmonizepolys_(_Float128 *, int *, harmonic []);

void	ikrand_(int *, double *);
void	ikrandp_(double *, double *);
void	ikrandm_(double *, double *);

void	msg(char *, ...);

polygon	*new_poly(int);
void	free_poly(polygon *);
int	room_poly(polygon **, int, int, int);
void	memmsg(void);

vertices	*new_vert(int);
void	free_vert(vertices *);

void	parse_args(int, char *[]);

int	parse_fopt(void);

#ifdef	GCC
int	partition_poly(polygon **, int npolys, polygon *[npolys], _Float128, int, int, int, int, int *);
int	partition_gpoly(polygon *, int npolys, polygon *[npolys], _Float128, int, int, int, int *);
int	part_poly(polygon *, int npolys, polygon *[npolys], _Float128, int, int, int, int *, int *);
int     pixel_list(int npoly, polygon *[npoly], int max_pixel, int [max_pixel], int [max_pixel]);
int     grow_poly(polygon **, int npolys, polygon *[npolys], _Float128, _Float128, int *);
#else
int	partition_poly(polygon **, int npolys, polygon *[/*npolys*/], _Float128, int, int, int, int, int *);
int	partition_gpoly(polygon *, int npolys, polygon *[/*npolys*/], _Float128, int, int, int, int *);
int	part_poly(polygon *, int npolys, polygon *[/*npolys*/], _Float128, int, int, int, int *, int *);
int     pixel_list(int npoly, polygon *[/*npoly*/], int max_pixel, int [/*max_pixel*/], int [/*max_pixel*/]);
int     grow_poly(polygon **, int npolys, polygon *[/*npolys*/], _Float128, _Float128, int *);
#endif

int     pixel_start(int, char);

_Float128	places(_Float128, int);
int     poly_cmp(polygon **, polygon **);

#ifdef	GCC
int	poly_id(int npoly, polygon *[npoly], _Float128, _Float128, long long **, _Float128 **);
void	poly_sort(int npoly, polygon *[npoly], char);
#else
int	poly_id(int npoly, polygon *[/*npoly*/], _Float128, _Float128, long long **, _Float128 **);
void	poly_sort(int npoly, polygon *[/*npoly*/], char);
#endif


int	prune_poly(polygon *, _Float128);
int	trim_poly(polygon *);
int	touch_poly(polygon *);

int	rdangle(char *, char **, char, _Float128 *);

#ifdef	GCC
int	rdmask(char *, format *, int npolys, polygon *[npolys]);
#else
int	rdmask(char *, format *, int npolys, polygon *[/*npolys*/]);
#endif

void	rdmask_(void);

int	rdspher(char *, int *, harmonic **);

void	scale(_Float128 *, char, char);
void	scale_azel(azel *, char, char);
void	scale_vert(vertices *, char, char);

#ifdef	GCC
int	search(int n, _Float128 [n], _Float128);
#else
int	search(int n, _Float128 [/*n*/], _Float128);
#endif

#ifdef	GCC
int	snap_polys(format *fmt, int npoly, polygon *poly[npoly], int, _Float128, _Float128, _Float128, _Float128, _Float128, int, char *);
#else
int	snap_polys(format *fmt, int npoly, polygon *poly[/*npoly*/], int, _Float128, _Float128, _Float128, _Float128, _Float128, int, char *);
#endif
int	snap_poly(polygon *, polygon *, _Float128, _Float128);
int	snap_polyth(polygon *, polygon *, _Float128, _Float128, _Float128);

int	split_poly(polygon **, polygon *, polygon **, _Float128);
#ifdef	GCC
int	fragment_poly(polygon **, polygon *, int, int npolys, polygon *[npolys], _Float128, char);
#else
int	fragment_poly(polygon **, polygon *, int, int npolys, polygon *[/*npolys*/], _Float128, char);
#endif

int	strcmpl(const char *, const char *);
int	strncmpl(const char *, const char *, size_t);

int	strdict(char *, char *[]);
int	strdictl(char *, char *[]);

#ifdef	GCC
int	vmid(polygon *, _Float128, int nv, int nve, vec [nv * nve], int [nv], int [nv], int *, vec **);
int	vmidc(polygon *, int nv, int nve, vec [nv * nve], int [nv], int [nv], int *, vec **);
#else
int	vmid(polygon *, _Float128, int nv, int nve, vec [/*nv * nve*/], int [/*nv*/], int [/*nv*/], int *, vec **);
int	vmidc(polygon *, int nv, int nve, vec [/*nv * nve*/], int [/*nv*/], int [/*nv*/], int *, vec **);
#endif

_Float128	weight_fn(_Float128, _Float128, char *);
_Float128	rdweight(char *);

_Float128	twoqz_(_Float128 *, _Float128 *, int *);
_Float128	twodf100k_(_Float128 *, _Float128 *);
_Float128	twodf230k_(_Float128 *, _Float128 *);

int     which_pixel(_Float128, _Float128, int, char);

#ifdef	GCC
void	wrangle(_Float128, char, int, size_t str_len, char [str_len]);
#else
void	wrangle(_Float128, char, int, size_t str_len, char [/*str_len*/]);
#endif

#ifdef	GCC
_Float128	wrho(_Float128, _Float128, int lmax, int, harmonic w[NW], _Float128, _Float128);
#else
_Float128	wrho(_Float128, _Float128, int lmax, int, harmonic w[/*NW*/], _Float128, _Float128);
#endif

_Float128	wrho_(_Float128 *, _Float128 *, harmonic *, int *, int *, int *, int *, _Float128 *, _Float128 *);

#ifdef	GCC
int	wrmask(char *, format *, int npolys, polygon *[npolys]);
int	wr_circ(char *, format *, int npolys, polygon *[npolys], int);
int	wr_edge(char *, format *, int npolys, polygon *[npolys], int);
int	wr_rect(char *, format *, int npolys, polygon *[npolys], int);
int	wr_poly(char *, format *, int npolys, polygon *[npolys], int);
int	wr_dpoly(char *, format *, int npolys, polygon *[npolys], int, long long[npolys]);
int	wr_Reg(char *, format *, int npolys, polygon *[npolys], int);
int	wr_area(char *, format *, int npolys, polygon *[npolys], int);
int	wr_id(char *, int npolys, polygon *[npolys], int);
int	wr_midpoint(char *, format *, int npolys, polygon *[npolys], int);
int	wr_weight(char *, format *, int npolys, polygon *[npolys], int);
int     wr_healpix_weight(char *, format *, int numweight, _Float128 [numweight]);
int	wr_list(char *, format *, int npolys, polygon *[npolys], int);
int	discard_poly(int npolys, polygon *[npolys]);
#else
int	wrmask(char *, format *, int npolys, polygon *[/*npolys*/]);
int	wr_circ(char *, format *, int npolys, polygon *[/*npolys*/], int);
int	wr_edge(char *, format *, int npolys, polygon *[/*npolys*/], int);
int	wr_rect(char *, format *, int npolys, polygon *[/*npolys*/], int);
int	wr_poly(char *, format *, int npolys, polygon *[/*npolys*/], int);
int	wr_Reg(char *, format *, int npolys, polygon *[/*npolys*/], int);
int	wr_area(char *, format *, int npolys, polygon *[/*npolys*/], int);
int	wr_id(char *, int npolys, polygon *[/*npolys*/], int);
int	wr_midpoint(char *, format *, int npolys, polygon *[/*npolys*/], int);
int	wr_weight(char *, format *, int npolys, polygon *[/*npolys*/], int);
int     wr_healpix_weight(char *, format *, int numweight, _Float128 [/*numweight*/]);
int	wr_list(char *, format *, int npolys, polygon *[/*npolys*/], int);
int	discard_poly(int npolys, polygon *[/*npolys*/]);
#endif

int	wrrrcoeffs(char *, _Float128, _Float128 [2], _Float128 [2]);

#ifdef	GCC
int	wrspher(char *, int lmax, harmonic [NW]);
#else
int	wrspher(char *, int lmax, harmonic [/*NW*/]);
#endif

#endif	/* MANGLEFN_H */
