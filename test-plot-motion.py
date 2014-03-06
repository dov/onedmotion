# An example of how to use the motion profile library.
# Plot the motion with matplotlib.

from onedmotion import MotionProfile

"""Testing"""
m = MotionProfile(start_time = 100.,
                  start_pos = 0.,
                  max_velocity = 7.5,
                  acceleration = 0.15,
                  deceleration = 0.5,
                  distance = 500.)

# Plot the motion with pylab
from pylab import *
t = []
x = []
v = []
for i in range(300):
  t += [i]
  x += [m.GetPos(i)]
  v += [m.GetVelocity(i)]

plot(t,x,'r',label='Position')
ylabel('Position')
t2 = twinx()
t2.plot(t,v,'g',label='Velocity')
t2.set_ylabel('Velocity')
show()

