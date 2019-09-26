# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 14:26:23 2019

@author: MV
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 07:25:47 2019

@author: MV
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 14:45:46 2019

@author: MV
"""
import numpy as np

#learning curve
gamma = 0.4
alpha = 0.02

location_to_state = {'beg': 0,
                     'spend': 1,
                     'noSpend': 2,
                     'end':3,
                     'node':4
                     
            
                    
                     
                     }
nothing=5+0
#coeLand1=0.4179
#coeReact1 =0.5362 
#coeClick1 =0.1674
coeLand1=--0.46801
coeReact1 =-1.79781
coeClick1 =0.47247
budget=1
#targeted_cost = 10
#covClick1=0.51479
#covLand1=0.01352
#covReact1=-0.41653
#cpc= targeted_cost/targeted_conversion
#budget formula: budget = scale*conversion

test=['buy',4.3]
state_to_location = {state: location for location, state in location_to_state.items()}

def route(starting_location,ending_location,cpc):
    cpc=cpc
    day2_increase = (budget*coeClick1+budget*coeReact1+budget*coeLand1)*cpc
    function = (budget*0.4285) + budget*0.2686 + 1.0910*budget
    actions = [0,1,2,3]
    R = np.array([[0,-budget,budget,0,0],
              [0,0,0,day2_increase,0],
              [0,0,0,budget,0],
              [0,0,0,0,1],
              [0,0,0,1,0]
              ])

    print('cpc:' + str(cpc))
    R_new = np.copy(R)
    ending_state = location_to_state[ending_location]
    R_new[ending_state, ending_state] = 10000
    Q = np.array(np.zeros([5,5]))
    for i in range(10000):
        current_state = np.random.randint(0,5)
        playable_actions = []
        for j in range(5):
            if R_new[current_state, j] != 0:
                playable_actions.append(j)
        next_state = np.random.choice(playable_actions)
        TD = R_new[current_state, next_state] + gamma * Q[next_state, np.argmax(Q[next_state,])] - Q[current_state, next_state]
        Q[current_state, next_state] = Q[current_state, next_state] + alpha * TD
    route = [starting_location]
    next_location = starting_location
    while (next_location != ending_location):
        starting_state = location_to_state[starting_location]
        next_state = np.argmax(Q[starting_state,])
        next_location = state_to_location[next_state]
        route.append(next_location)
        starting_location = next_location
        print(route)
        
    return route

def best_route(starting_location, intermediary_location, ending_location):
    return route(starting_location, intermediary_location) + route(intermediary_location, ending_location)[1:]

cpc_init=2
while(cpc_init>0):
    print('Route:')
    route('beg','end',cpc_init)
    cpc_init= cpc_init -0.1




