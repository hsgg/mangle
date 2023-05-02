#ifndef HIGHPRECISIONMATH_H
#define HIGHPRECISIONMATH_H 1


#define FLOATQ_IS_QUADMATH 1


#ifdef FLOATQ_IS_QUADMATH
/* FloatQ is quad precision */

typedef _Float128 FloatQ;

#define Q "Q"

#define sqrtQ sqrtq

#define sinQ sinq
#define cosQ cosq
#define tanQ tanq

#define asinQ asinq
#define acosQ acosq
#define atanQ atanq
#define atan2Q atan2q


#else
/* FloatQ is long double */

typedef long double FloatQ;

#define Q "L"

#define sqrtQ sqrtl

#define sinQ sinl
#define cosQ cosl
#define tanQ tanl

#define asinQ asinl
#define acosQ acosl
#define atanQ atanl
#define atan2Q atan2l


#endif


#endif
