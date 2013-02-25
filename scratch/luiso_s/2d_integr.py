import numpy
from iotbx.detectors import ImageFactory
from matplotlib import pyplot as plt

image = ImageFactory( 'thaumatin_die_M1S5_1_0001.img' )
image.read()

nfast = image.parameters['SIZE1']
nslow = image.parameters['SIZE2']

data = image.get_raw_data()
print '01 nfast, nslow =', nfast, nslow
data2d = numpy.reshape( numpy.array( data, dtype = float ), ( nfast , nslow ) )

f_from = int( nfast * 2 / 6 )  #   temporarily using
f_to = int( nfast / 2 )  #         only part of the image
s_from = int( nslow * 2 / 6 )  #   so I can code a bit faster
s_to = int( nslow / 2 )  #
nfast = f_to - f_from  #           It is taking way to long if we
nslow = s_to - s_from  #           use the entire image

coordlist = [[139, 227]  , [147, 235], [157, 245], [166, 253]]

data2d = data2d[f_from:f_to, s_from:f_to]
print 'new nfast, nslow =', nfast, nslow

data2dsmoth = numpy.zeros( nfast * nslow, dtype = float ).reshape( nfast, nslow )
diffdata2d = numpy.zeros( nfast * nslow, dtype = float ).reshape( nfast, nslow )
pointmask = numpy.zeros( nfast * nslow, dtype = float ).reshape( nfast, nslow )


print "nslow, nfast =", nslow, nfast
print "max(data2d) =", numpy.max( data2d )
print "min(data2d) =", numpy.min( data2d )
data2dtmp = data2d
for times in range( 5 ):
    for f in range( 3, nfast - 3 ):
        for s in range( 1, nslow - 1 ):
            pscan = float( numpy.sum( data2dtmp[f - 1:f + 2, s - 1:s + 2] ) / 9.0 )
            data2dsmoth[f, s] = pscan
    data2dtmp = data2dsmoth

data2dsmoth = data2dsmoth + 10.0
print "max(data2dsmoth) =", numpy.max( data2dsmoth )
print "min(data2dsmoth) =", numpy.min( data2dsmoth )

for f in range( 1, nfast - 1 ):
    for s in range( 1, nslow - 1 ):
        if data2d[f, s] > data2dsmoth[f, s]:
            diffdata2d[f, s] = 1

print "max(diffdata2d) =", numpy.max( diffdata2d )
print "min(diffdata2d) =", numpy.min( diffdata2d )
print "__________________________________________"

for coord in coordlist:
    pointmask[coord[0], coord[1]] = 1

print "Plotting data2d"
plt.imshow( numpy.transpose( data2d ), interpolation = "nearest" )
plt.show()

print "Plotting data2dsmoth"
plt.imshow( numpy.transpose( data2dsmoth ), interpolation = "nearest" )
plt.show()

print "Plotting diffdata2d"
plt.imshow( numpy.transpose( diffdata2d ), interpolation = "nearest" )
plt.show()

print "Plotting pointmask"
plt.imshow( numpy.transpose( pointmask ), interpolation = "nearest" )
plt.show()

