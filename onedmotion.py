# onedmotion profile
#
# Copyright (c) 2014 Dov Grobgeld <https://github.com/dov>
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.
# 
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import math

class MotionProfile:
  def __init__(self,
               start_time=0,
               start_pos=0,
               start_velocity = 0,
               end_velocity = 0,
               distance = 100,
               max_velocity = 50,
               acceleration = 50,
               deceleration = 50):
    """Create a motion of a linear motion from `start_pos` at distance `distance`.

    To simulate a negative motion all of the following entities need to be inverted:

      - start_velocity
      - end_velocity
      - distance
      - acceleration
      - deceleration
      - max_velocity (which really should be called requested peak velocity)
    """
    self.start_time = start_time
    self.start_pos = start_pos
    self.start_velocity = start_velocity
    self.end_velocity = start_velocity
    self.distance = distance
    self.acceleration = 1.0*acceleration
    self.deceleration = 1.0*deceleration

    start_velocity_to_full_speed_time = 1.0*(max_velocity-start_velocity) / acceleration
    self.accel_end_time = self.start_time + start_velocity_to_full_speed_time
    self.accel_accumulated_dist = ( self.start_velocity * self.start_time
                                 + start_velocity_to_full_speed_time ** 2 /2. * self.acceleration)

    full_speed_to_end_velocity_time = 1.0*(max_velocity-self.end_velocity) / self.deceleration
    decel_dist = self.deceleration * full_speed_to_end_velocity_time ** 2 /2.
    self.uniform_dist = self.distance - self.accel_accumulated_dist - decel_dist

    # If the uniform distance is negative, then we never reach the
    # maximum speed, and we instead do a triangle motion.
    if self.uniform_dist * self.distance < 0:
      # Find intersection between the acceleration and the deceleration position
      # and velocity.
      #    1/2 * Ta^2 * a + 1/2 * Td^2 * d = D
      #    Ta*a - Td * d = 0
      #
      # Ta*a is the max speed.
      #
      # Solving this equation system for Ta yields:
      #
      #    Ta = sqrt( (2*d*D)/(a*(a+d)) )
      #
      tmax = math.sqrt((2 * self.deceleration * self.distance) /
                       (self.acceleration * (self.acceleration + self.deceleration)))

      self.accel_end_time = self.start_time + tmax
      self.max_velocity = self.start_velocity + tmax*self.acceleration

      self.uniform_dist = 0
      self.accel_accumulated_dist = self.start_time * self.start_velocity + tmax**2/2 * self.acceleration
      full_speed_to_end_velocity_time = (self.max_velocity - self.end_velocity) / self.deceleration
    else:
      self.max_velocity = max_velocity

    self.uniform_accumulated_dist = self.accel_accumulated_dist + self.uniform_dist
    self.uniform_end_time = self.accel_end_time + self.uniform_dist / self.max_velocity
    self.decel_end_time = self.uniform_end_time + full_speed_to_end_velocity_time
    self.accel_end_pos = self.get_pos(self.accel_end_time)
    self.uniform_end_pos = self.get_pos(self.uniform_end_time)
    self.decel_end_pos = self.get_pos(self.decel_end_time)

  def get_pos(self,
              time):
    """Get the position of the system at time time"""
    if time < self.start_time:
      return self.start_pos
    elif time < self.accel_end_time:
      return self.start_pos + (time-self.start_time)**2 * self.acceleration/2.
    elif time < self.uniform_end_time:
      return self.start_pos + self.accel_accumulated_dist + (time - self.accel_end_time) * self.max_velocity
    elif time < self.decel_end_time:
      return self.start_pos + self.distance - (self.decel_end_time-time)**2 * self.deceleration/2.
    else:
      return self.start_pos + self.distance + (time - self.decel_end_time) * self.end_velocity

  def get_velocity(self,
                  time):
    """Get the velocity of the system at time `time`"""
    if time < self.start_time:
      return self.start_velocity
    elif time < self.accel_end_time:
      return (self.start_velocity + self.acceleration * (time-self.start_time))
    elif time < self.uniform_end_time:
      return self.max_velocity
    elif time < self.decel_end_time:
      return self.max_velocity - self.deceleration * (time-self.uniform_end_time)
    else:
      return self.end_velocity

  def get_destination(self):
    return self.start_pos + self.distance

  def get_end_time(self):
    return self.decel_end_time
  
  def get_time_from_position(self, pos):
    epsilon = 1e-5

    if self.max_velocity < 0:
      if pos > self.start_pos:
        return None
      elif pos > self.accel_end_pos:
        return self.start_time + (math.sqrt(2 * self.acceleration * (pos - self.start_pos) + self.start_velocity**2) - self.start_velocity) / -self.acceleration
      elif pos > self.uniform_end_pos:
        return self.accel_end_time + 1.0*(pos - self.accel_end_pos) / self.max_velocity
      elif pos > self.decel_end_pos:
        return self.uniform_end_time + ((math.sqrt(2 * self.deceleration* (self.uniform_end_pos - pos ) + self.max_velocity**2) + self.max_velocity) / (self.deceleration))
      elif pos > self.decel_end_pos:
        return self.decel_end_time
      else:
        return None
    else:
      if pos < self.start_pos:
        return None
      elif pos < self.accel_end_pos:
        return self.start_time + (math.sqrt(2 * self.acceleration * (pos - self.start_pos) + self.start_velocity**2) - self.start_velocity) / self.acceleration
      elif pos < self.uniform_end_pos:
        return self.accel_end_time + 1.0*(pos - self.accel_end_pos) / self.max_velocity
      elif pos < self.decel_end_pos:
        return self.uniform_end_time + ((math.sqrt(-2 * self.deceleration* (pos - self.uniform_end_pos) + self.max_velocity**2) - self.max_velocity) / (-self.deceleration))
      elif pos < self.decel_end_pos:
        return self.decel_end_time
      else:
        return None

  def plot(self,
           N = 200,
           pos_style='r',
           vel_style = 'g',
           ax=None,
           legend_loc=0):
    '''Plot a graph of the motion with matplotlib. Returns the axis and the
    graphs'''
    import matplotlib.pyplot as plt
    tAry = []
    xAry = []
    vAry = []
    tEnd = self.get_end_time()
    
    for i in range(N):
      t = tEnd / N *i 
      tAry += [t]
      xAry += [self.get_pos(t)]
      vAry += [self.get_velocity(t)]
    
    if ax is None:
      ax = plt.gca()
    g1 = ax.plot(tAry,xAry,'r',label='Position')[0]
    ax.set_ylabel('Position')
    ax1 = ax.twinx()
    g2 = ax1.plot(tAry,vAry,'g',label='Velocity')[0]
    ax1.set_ylabel('Velocity')

    ax.legend([g1,g2],
              [v.get_label() for v in [g1,g2]],
              loc=legend_loc)
    return ax,[g1,g2]

if __name__=='__main__':
  import matplotlib.pyplot as plt

  m = MotionProfile(start_time = 0.,
                  start_pos = 0.,
                  max_velocity = 7.5,
                  acceleration = 0.3,
                  deceleration = 0.3,
                  distance = 500.)
  ax,gg = m.plot()
  
  plt.show()
