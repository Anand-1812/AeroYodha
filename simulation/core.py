class UAV:
    def __init__(self, uid, pos, vel, priority=1):
        self.uid = uid
        self.pos = pos      
        self.vel = vel      
        self.priority = priority

    def step(self, dt=1.0):
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
