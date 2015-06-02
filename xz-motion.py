# This is a simulation of a two coupled motions through simpy. The
# xaxis is the position of a car that is driving back and forth
# between positions 0 and 1000. At position 500 there is a platform
# that needs to be raised for the car to continue.
#
# Platform at lower position
#
#             |-\_                    ____________
#             o--o_____________ _____
#
#
#
# Platform at upper position
#                                            |-\_                      
#                               _____ _______o--o____
#
#                 _____________
#
# Dov Grobgeld <dov.grobgeld@gmail.com>
# 2015-06-02 Tue

import matplotlib.pyplot as plt
from onedmotion import MotionProfile
import simpy

class MotionRequest(object):
    def __init__(self,
                 destination):
        self.destination = destination

class SleepRequest(object):
    def __init__(self,
                 time):
        self.time = time

class BlockRequest(object):
    def __init__(self, block):
        self.block = block

class NotifyRequest(object):
    def __init__(self, block):
        self.block = block

class Logger:
    def __init__(self):
        self.log_events = []

    def log_axis_change_state(self, axis, motion_profile, time):
        self.log_events += [(axis, motion_profile, time)]

    def get_motion_profile(self, axis, time):
        """Do a linear search for the motion profile that contain the above time"""
        axis_events = [(mp,t) for ax,mp,t in self.log_events
                       if ax==axis]
        if len(axis_events)==0:
            return None
        
        for mp,t in axis_events:
            if time <= mp.decel_end_time:
                return mp
        return mp

class Axis:
    def __init__(self,
                 simenv,
                 axis,
                 init_pos=0,
                 init_velocity=0,
                 logger=None,
                 max_velocity=10.,
                 acceleration=0.5):
        '''Define an axis with a given profile'''
        self.axis = axis
        self.pos = init_pos
        self.velocity = init_velocity
        self.simenv = simenv
        self.action_queue = simpy.Store(simenv)
        self.max_velocity = max_velocity
        self.acceleration = acceleration
        self.logger = logger
        self.last_destination = 0

    def add_motion(self, destination):
        """Add a new motion to the motion file"""
        print 'Adding request to ', destination
        self.action_queue.put(MotionRequest(destination))

    def add_block(self, block):
        """Add a block for a request"""
        self.action_queue.put(BlockRequest(block))

    def add_notifier(self):
        block = simpy.Store(self.simenv)
        self.action_queue.put(NotifyRequest(block))
        return block

    def move_to(self, destination):
        """Build motion request either from the end of the last pos in
        queue or from current position"""
        self.add_motion(destination)
                                 
    def sleep(self, time):
        self.action_queue.put(SleepRequest(time))

    def process(self):
        '''In the main loop of the axis it receives and processes requests.
        The three requests supported are Block, which makes the axis
        block until it is notified; Notify which notifies all axes
        waiting for the notification; Motion which does a blocking
        motion (no events may be sent during the motion profile).
        '''
        env = self.simenv

        while True:
            with self.action_queue.get() as req:
                r = yield req
                if type(r) is BlockRequest:
                    print 'Waiting for block to clear!'
                    yield r.block.get()
                    print 'block cleared!'
                elif type(r) is NotifyRequest:    
                    yield r.block.put(mp)
                    print 'notifying!'
                elif type(r) is SleepRequest:    
                    yield env.timeout(r.time)
                elif type(r) is MotionRequest:
                    distance = r.destination - self.pos
                    s = -1. if distance < 0 else 1.
                    print 'Starting motion from ',self.pos, 'destination=',r.destination
                    mp = MotionProfile(start_time = env.now,
                                       start_pos = self.pos,
                                       distance = distance,
                                       max_velocity = s*self.max_velocity,
                                       acceleration = s*self.acceleration,
                                       deceleration = s*self.acceleration)
                    self.logger.log_axis_change_state(self.axis, mp, env.now)
                    yield env.timeout(mp.decel_end_time-mp.start_time)
                    self.pos = mp.get_destination()

logger = Logger()
env = simpy.Environment()
xAxis = Axis(env,0,logger=logger)
zAxis = Axis(env,1,logger=logger,max_velocity=1)
env.process(xAxis.process())
env.process(zAxis.process())

# A simulation of a car driving back and forth (x) and a platform (z)
# that need to place the car between two different levels.
for i in range(2):
    xAxis.move_to(500)
    zAxis.add_block(xAxis.add_notifier())
    zAxis.move_to(100)
    xAxis.add_block(zAxis.add_notifier())
    xAxis.move_to(1000)
    xAxis.sleep(100)
    xAxis.move_to(500)
    zAxis.add_block(xAxis.add_notifier())
    zAxis.move_to(0)
    xAxis.add_block(zAxis.add_notifier())
    xAxis.move_to(0)
    xAxis.sleep(200)

EndTime = 2000
env.run(until=EndTime)
print 'Done simulation'

# Plot the motion
tAry = []
pxAry = []
pzAry = []
vxAry = []
vzAry = []

# Output the events
for ax,mp,time in logger.log_events:
    print time,ax, mp.start_time, mp

# Plot them
for i in range(0,EndTime,1):
    t = i
    tAry+= [t]
    mp = logger.get_motion_profile(0, t)
    pxAry += [mp.get_pos(t)]
    vxAry += [mp.get_velocity(t)]

    mp = logger.get_motion_profile(1, t)
    if mp is not None:
        pzAry += [mp.get_pos(t)]
        vzAry += [mp.get_velocity(t)]

plt.subplot(211)
plt.title('Coupled motion')
plt.margins(0,0.05)
plt.plot(tAry,pxAry,label='x')
if len(pzAry):
    plt.plot(tAry,pzAry,label='z')
plt.ylabel('Position')
plt.legend()
plt.subplot(212)
plt.margins(0,0.05)
plt.plot(tAry,vxAry,label='x')
if len(vzAry):
    plt.plot(tAry,vzAry,label='z')
plt.legend()
plt.ylabel('Velocity')
plt.xlabel('Time')
plt.show()
