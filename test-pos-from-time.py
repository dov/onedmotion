from onedmotion import MotionProfile

if 0:
  m = MotionProfile(start_time = 0.,
                    start_pos = 0.,
                    max_velocity = 7.5,
                    acceleration = 0.5,
                    deceleration = 0.5,
                    distance = 500.)
  
  end_time = m.get_end_time()
  epsilon = 1e-8
  for i in range(10):
    t = 1.0*end_time/10.0*i
    x = m.get_pos(t)
    tout = m.get_time_from_position(x)
    print(t,x,tout)
    assert(abs(t-tout)<epsilon)

if 1:
  m = MotionProfile(start_time = 0.,
                    start_pos = 0.,
                    max_velocity = -7.5,
                    acceleration = -0.5,
                    deceleration = -0.5,
                    distance = -500.)
  
  end_time = m.get_end_time()
  print('end_time = ', end_time)
  epsilon = 1e-8
  for i in range(10):
    t = 1.0*end_time/10.0*i
    x = m.get_pos(t)
    tout = m.get_time_from_position(x)
    print(t,x,tout)
    assert(abs(t-tout)<epsilon)
  
