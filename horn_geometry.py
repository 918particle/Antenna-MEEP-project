import numpy as np

def create_box_inner(a):
	x = [a,0,0,a]
	y = [-a/2,-a/2,a/2,a/2]
	return (x,y)
def create_box_outer(a,dx):
	x = [a,-dx,-dx,a]
	y = [a/2+dx,a/2+dx,-a/2-dx,-a/2-dx]
	return (x,y)
def create_upper_side(a,c,d,n,dy):
	k1 = a/2
	k2 = 1.0/(c-a)*np.log(2*d/a)
	x = []
	y = []
	for i in range(n):
		xi = a+i/n*c
		x.append(xi)
		y.append(k1*np.exp(k2*(xi-a)))
	for i in range(n-1,-1,-1):
		xi = xi = a+i/n*c
		x.append(xi)
		y.append(k1*np.exp(k2*(xi-a))+dy)
	return(x,y)
def create_lower_side(a,c,d,n,dy):
	(x,y) = create_upper_side(a,c,d,n,dy)
	n = len(x)
	y = [-y[i] for i in range(n)]
	return(x,y)
def create_horn(a,c,d,n,dy):
	k1 = a/2
	k2 = 1.0/(c-a)*np.log(2*d/a)
	x = []
	y = []
	for i in range(n):
		xi = a+i/n*c
		x.append(xi)
		y.append(k1*np.exp(k2*(xi-a))+dy)
	for i in range(n-1,-1,-1):
		xi = xi = a+i/n*c
		x.append(xi)
		y.append(-(k1*np.exp(k2*(xi-a))+dy))
	x.append(0)
	y.append(-a)
	x.append(0)
	y.append(a)
	return (x,y)

a = 1.0
c = 15.9
d = 4.25
th = 0.5
n = 100

(xo,yo) = create_box_outer(a,th)
(xi,yi) = create_box_inner(a)
(xsu,ysu) = create_upper_side(a,c,d,n,th)
(xsl,ysl) = create_lower_side(a,c,d,n,th)
(xhorn,yhorn) = create_horn(a,c,d,n,th)

#n_box = len(xo)
#for i in range(4):
#	print(xi[i],yi[i])
#for i in range(4):
#	print(xo[i],yo[i])
n = len(xsu)
for i in range(n):
	print(xsu[i],ysu[i])
#n = len(xsl)
#for i in range(n):
#	print(xsl[i],ysl[i])
#n = len(xhorn)
#for i in range(n):
#	print(xhorn[i],yhorn[i])