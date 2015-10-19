# An example of how to use the motion profile library.
# Plot the motion with matplotlib.

from onedmotion import MotionProfile
import matplotlib.pyplot as plt

"""Testing"""
ax = None

for sp,dir in enumerate((-1,1)):
  plt.subplot(2,1,sp)
  m = MotionProfile(start_time = 0.,
                    start_pos = 0.,
                    max_velocity = 7.5*dir,
                    acceleration = 0.05*dir,
                    deceleration = 0.05*dir,
                    distance = 2000.*dir)
  m.plot()
  plt.title('Dir=%d'%dir)

plt.show()

## Plot the motion with pylab
#from pylab import *
#tAry = []
#xAry = []
#vAry = []
#N = 200
#tEnd = m.get_end_time()
#print tEnd
#
#for i in range(N):
#  t = tEnd / N *i 
#  tAry += [t]
#  xAry += [m.get_pos(t)]
#  vAry += [m.get_velocity(t)]
#
#plot(tAry,xAry,'r',label='Position')
#ylabel('Position')
#t2 = twinx()
#t2.plot(tAry,vAry,'g',label='Velocity')
#t2.set_ylabel('Velocity')
#show()

