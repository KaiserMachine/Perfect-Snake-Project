from gym.envs.registration import register

register(
    id='poison_triple_v0',
    entry_point='poison_triple.envs:SnakeEnv',
)
