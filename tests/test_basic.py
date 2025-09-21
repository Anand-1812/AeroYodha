from simulation.core import UAV

def test_uav_step():
    u = UAV("U1", [0,0], [1,0])
    u.step()
    assert u.pos == [1,0]
