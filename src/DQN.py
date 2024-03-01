import tensorflow as tf
import numpy as np
import random

class DQN(tf.keras.Model):
    def __init__(self, state_shape, num_actions, buffer_size=10000, batch_size=32, gamma=0.99):
        super(DQN, self).__init__()
        self.state_shape = state_shape
        self.num_actions = num_actions
        self.buffer_size = buffer_size
        self.batch_size = batch_size
        self.gamma = gamma

        self.replay_buffer = []

        self.dense1 = tf.keras.layers.Dense(64, activation='relu')
        self.dense2 = tf.keras.layers.Dense(64, activation='relu')
        self.dense3 = tf.keras.layers.Dense(num_actions)

        self.optimizer = tf.keras.optimizers.Adam()

    def call(self, state):
        x = self.dense1(state)
        x = self.dense2(x)
        q_values = self.dense3(x)
        return q_values

    def store_transition(self, state, action, reward, next_state, done):
        self.replay_buffer.append((state, action, reward, next_state, done))

        if len(self.replay_buffer) > self.buffer_size:
            self.replay_buffer.pop(0)

    def train(self):
        minibatch = random.sample(self.replay_buffer, min(len(self.replay_buffer), self.batch_size))

        states, actions, rewards, next_states, dones = [], [], [], [], []
        for transition in minibatch:
            state, action, reward, next_state, done = transition
            states.append(state)
            actions.append(action)
            rewards.append(reward)
            next_states.append(next_state)
            dones.append(done)

        states = np.array(states)
        actions = np.array(actions)
        rewards = np.array(rewards)
        next_states = np.array(next_states)
        dones = np.array(dones)
        predicted_q_values = self.predict(next_states)

        target_q_values = rewards + (1 - dones[:, None]) * self.gamma * np.amax(predicted_q_values, axis=1)

        with tf.GradientTape() as tape:
            predicted_q_values = self(states)
            actions_one_hot = tf.one_hot(actions, self.num_actions)
            predicted_q_values_for_actions = tf.reduce_sum(predicted_q_values * actions_one_hot, axis=1)
            loss = tf.reduce_mean(tf.square(target_q_values - predicted_q_values_for_actions))

        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))