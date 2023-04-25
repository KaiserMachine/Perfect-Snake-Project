from gym.envs.registration import register

register(
    id='walls_v0',
    entry_point='walls.envs:SnakeEnv',
)
