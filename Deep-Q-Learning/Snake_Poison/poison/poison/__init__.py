from gym.envs.registration import register

register(
    id='poison-v0',
    entry_point='poison.envs:SnakeEnv',
)
