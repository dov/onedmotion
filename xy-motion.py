# A simulation of connected x and y motions through simpy

import matplotlib.pyplot as plt
from onedmotion import MotionProfile
import simpy

class MotionRequest(object):
    def __init__(self,
                 destination):
        self.destination = destination

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
        for ax,mp,t in self.log_events:
            if ax!=axis:
                continue
            if time <= mp.decel_end_time:
                return mp
        return mp

class Axis:
    def __init__(self, simenv, axis, init_pos=0, init_velocity=0, logger=None, max_velocity=10., Acceleration=0.5):
        self.axis = axis
        self.pos = init_pos
        self.velocity = init_velocity
        self.simenv = simenv
        self.action_queue = simpy.Store(simenv)
        self.max_velocity = max_velocity
        self.acceleration = acceleration
        self.logger = logger

    def AddMotion(self, destination):
        """Add a new motion to the motion file"""
        self.action_queue.put(MotionRequest(destination))

    def add_block(self, block):
        """Add a block for a request"""
        self.action_queue.put(BlockRequest(block))

    def AddNotifier(self):
        block = simpy.Store(self.simenv)
        self.action_queue.put(NotifyRequest(block))
        return block

    def move_to(self, destination):
        """Build motion request either from the end of the last pos in
        queue or from current position"""
        self.AddMotion(destination - self.last_destination)
                                 
    def Process(self):
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
                elif type(r) is MotionRequest:
                    distance = r.destination - self.pos
                    s = -1. if distance < 0 else 1.
                    mp = MotionProfile(start_time = env.now,
                                       start_pos = self.pos,
                                       distance = distance,
                                       max_velocity = s*self.max_velocity,
                                       acceleration = s*self.acceleration,
                                       deceleration = s*self.acceleration)
                    self.logger.log_axis_change_state(self.axis, mp, env.now)
                    yield env.timeout(mp.decel_end_time-mp.start_time)
                    self.pos = mp.get_destination()

class Clock:
    def __init__(self, simenv):
        self.simenv = simenv

    def Process(self):
        while 1:
            yield env.timeout(100)
            print env.now, "clock tick"

logger = Logger()
env = simpy.Environment()
xAxis = Axis(env,0,logger=logger)
yAxis = Axis(env,1,logger=logger)
env.process(xAxis.Process())
env.process(yAxis.Process())
#env.process(Clock(env).Process())

for i in range(5):
    xAxis.move_to(1000)
    xAxis.move_to(0)
    yAxis.add_block(xAxis.AddNotifier())
    yAxis.move_to(100*((i+1)%2))
    xAxis.add_block(yAxis.AddNotifier())

EndTime = 2000
env.run(until=EndTime)
print 'Done simulation'

# Plot the motion
tAry = []
pxAry = []
pyAry = []
vxAry = []
vyAry = []

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
    pyAry += [mp.get_pos(t)]
    vyAry += [mp.get_velocity(t)]

plt.subplot(211)
plt.title('Coupled motion')
plt.margins(0,0.05)
plt.plot(tAry,pxAry,label='x')
plt.plot(tAry,pyAry,label='y')
plt.ylabel('Position')
plt.legend()
plt.subplot(212)
plt.margins(0,0.05)
plt.plot(tAry,vxAry,label='x')
plt.plot(tAry,vyAry,label='y')
plt.legend()
plt.ylabel('Velocity')
plt.xlabel('Time')
plt.show()
