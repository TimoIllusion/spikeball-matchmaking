import tensorflow as tf
import numpy as np
import random
from itertools import combinations
from collections import deque, Counter
import pandas as pd

#TODO: rework state (should contain the history of the last 10 matchups and breaks)

# Initialize parameters
players = ['P' + str(i) for i in range(1, 6)]
max_rounds = 10
state_size = len(players)
alpha = 0.1
gamma = 0.9
epsilon = 0.1
num_epochs = 12

load_existing_model = False  # Set to True if you want to load an existing model
model_path = 'model.h5'
inference_mode = False  # Set to True if you want to run the model without training

if load_existing_model:
    model = tf.keras.models.load_model(model_path)
else:
    model = tf.keras.Sequential([
    tf.keras.layers.Dense(24, activation='relu', input_shape=(state_size,)),
    tf.keras.layers.Dense(24, activation='relu'),
    tf.keras.layers.Dense(1, activation='linear')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(lr=0.001), loss='mse')
    
if inference_mode == True:
    epsilon = 0.0 # no random guesses



# State to Neural Network input
def to_nn_input(state):
    state_vector = np.zeros(state_size)
    for player in state:
        idx = int(player[1:]) - 1
        state_vector[idx] = 1
    return state_vector

# Function to calculate next state and reward
def get_next_state(state, action):
    next_state = list(state)
    for player in action:
        next_state.remove(player)
    return tuple(sorted(next_state))

def get_complex_reward(state, action, break_counter, previous_matchups, previous_breaks):
    reward = 0
    if action in previous_matchups:
        reward -= 10
    for player in state:
        if player not in get_next_state(state, action) and player in previous_breaks:
            reward += 5
    return reward



# Main Q-learning loop
for epoch in range(num_epochs):
    
    matchups = []
    
    # Initialize break counters and previous matchups
    break_counter = Counter({player: 0 for player in players})
    previous_matchups = deque(maxlen=max_rounds)
    previous_breaks = deque(players, maxlen=len(players))
    
    
    for episode in range(max_rounds):
        print('Episode: ' + str(episode + 1))
        state = tuple(sorted(players))
        round_matchups = []

        while len(state) >= 4:  # As long as 4 or more players are left to be matched
            all_teams = list(combinations(state, 2))  # Update possible teams based on the current state

            if random.uniform(0, 1) < epsilon:
                action = random.choice(all_teams)
            else:
                q_values = [model.predict(to_nn_input(get_next_state(state, team)).reshape(1, -1))[0] for team in all_teams]
                action = all_teams[np.argmax(q_values)]
            
            next_state = get_next_state(state, action)

            if not inference_mode:
                reward = get_complex_reward(state, action, break_counter, previous_matchups, previous_breaks)
                next_possible_teams = list(combinations(next_state, 2))
                target = reward + gamma * np.max([model.predict(to_nn_input(get_next_state(next_state, team)).reshape(1, -1))[0] for team in next_possible_teams])
                history = model.fit(to_nn_input(next_state).reshape(1, -1), np.array([[target]]), epochs=1, verbose=0)
                print(f"Loss: {history.history['loss'][0]}")

            # Update state, previous matchups
            state = next_state
            previous_matchups.append(action)

            round_matchups.append(action)

        matchups.append(round_matchups)
    
# Save Model
if not inference_mode:
    model.save(model_path)


# Excel export here
# ...

print(matchups)
