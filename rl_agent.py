# rl_agent.py
import random
from collections import defaultdict


class QLearningAgent:
    def __init__(self):
        self.action_size = 5
        self.alpha = 0.1
        self.gamma = 0.95

        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995

        self.q_table = defaultdict(lambda: [0.0] * self.action_size)

    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)

        q_values = self.q_table[state]
        max_q = max(q_values)
        best_actions = [i for i, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def best_action(self, state):
        q_values = self.q_table[state]
        max_q = max(q_values)
        best_actions = [i for i, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state, done):
        current_q = self.q_table[state][action]
        next_max_q = 0 if done else max(self.q_table[next_state])

        new_q = current_q + self.alpha * (reward + self.gamma * next_max_q - current_q)
        self.q_table[state][action] = new_q