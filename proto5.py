# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 15:37:06 2019

@author: MV
"""

import numpy as np
import pandas as pd
from sklearn import linear_model
from google.cloud import bigquery
from datetime import date, timedelta
import os


def extract_data_fromBQ(gcp_credentials_path: str, q: str):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_credentials_path
    client = bigquery.Client("summerschool-253810")
    job_config = bigquery.QueryJobConfig()
    job_config.use_legacy_sql = False
    query = (q)
    query_job = client.query(query, job_config=job_config)
    result = query_job.result().to_dataframe()
    return result


query = """
SELECT facebookads_campaign_name as campaign_name,
facebookads_actions_link_click, facebookads_actions_landing_page_view, 
facebookads_actions_post_reaction,
facebookads_actions_leadgen_other as facebook_conversions,
common_cost, date, facebookads_actions_leadgen_other
FROM `summerschool-253810.tag_school.funnel_data_2019_*`
where sourceType="facebookads"
and dim_1cir7tmbddbjl_isBytek = 'true'
AND sourceName LIKE "Talent Garden Milano%"
"""

data = extract_data_fromBQ("../resources/gcp_credentials.json", query)

def get_coefficients(data: pd.DataFrame):
    # cleaning data thien's way and applying lr
    d3 = data

    d3['data_lagged7'] = (d3.sort_values(by=['date'], ascending=True)
                           .groupby(['campaign_name'])['common_cost'].shift(7))
    d3['data_lagged1'] = (d3.sort_values(by=['date'], ascending=True)
                           .groupby(['campaign_name'])['common_cost'].shift(1))
    d3['data_lagged2'] = (d3.sort_values(by=['date'], ascending=True)
                           .groupby(['campaign_name'])['common_cost'].shift(2))
    d3['data_lagged3'] = (d3.sort_values(by=['date'], ascending=True)
                           .groupby(['campaign_name'])['common_cost'].shift(3))


    d3=d3.dropna(axis=1, how='all')

    d3=d3.dropna(subset=['data_lagged7','data_lagged1','data_lagged2','data_lagged3'])
    d_final=d3[['campaign_name','date','data_lagged1','data_lagged7',
                'data_lagged2','facebookads_actions_post_reaction','facebookads_actions_landing_page_view',
                'facebookads_actions_link_click','facebookads_actions_leadgen_other']]


    X = d_final[data.columns & ['facebookads_actions_post_reaction',
            'facebookads_actions_landing_page_view',
             "facebookads_actions_link_click" ]]  # here we have 2 variables for multiple regression. If you just want to use one variable for simple linear regression, then use X = df['Interest_Rate'] for example.Alternatively, you may add additional variables within the brackets
    Y = d_final['data_lagged1']

    # with sklearn
    regr = linear_model.LinearRegression()
    regr.fit(X, Y)
    print('Intercept: \n', regr.intercept_)
    print('Coefficients: \n', regr.coef_)

    from regressors import stats
    print("coef_pval:\n", stats.coef_pval(regr, X, Y))

    return {
        'facebookads_actions_post_reaction': regr.coef_[0],
        'facebookads_actions_landing_page_view': regr.coef_[1],
        "facebookads_actions_link_click": regr.coef_[2]
    }


coefs = get_coefficients(data)


coeLand1 = coefs['facebookads_actions_landing_page_view']
coeReact1 = coefs['facebookads_actions_post_reaction']
coeClick1 = coefs["facebookads_actions_link_click"]


gamma = 0.4
alpha = 0.02

location_to_state = {'beg': 0,
                     'spend': 1,
                     'noSpend': 2,
                     'end':3
                     
            
                    
                     
                     }
nothing=5+0
#coeLand1=0.4179
#coeReact1 =0.5362 
#coeClick1 =0.1674
coeLand1=-0.46801
coeReact1 =1.79781
coeClick1 =0.47247
budget=1
#targeted_cost = 10
#covClick1=0.51479
#covLand1=0.01352
#covReact1=-0.41653
#cpc= targeted_cost/targeted_conversion
#budget formula: budget = scale*conversion
data_store=[]
result_store=[]
test=['buy',4.3]
state_to_location = {state: location for location, state in location_to_state.items()}

def route(starting_location,ending_location,cpc):
    cpc=cpc
    day2_increase = (budget*coeClick1+budget*coeReact1+budget*coeLand1)*cpc
    function = (budget*0.4285) + budget*0.2686 + 1.0910*budget
    actions = [0,1,2,3]
    R = np.array([[0,-budget,budget,0],
              [0,0,0,day2_increase],
              [0,0,0,budget],
              [0,0,1,0],
              ])

    print('cpc:' + str(cpc))
    R_new = np.copy(R)
    ending_state = location_to_state[ending_location]
    R_new[ending_state, ending_state] = 10000
    Q = np.array(np.zeros([4,4]))
    for i in range(10000):
        current_state = np.random.randint(0,4)
        playable_actions = []
        for j in range(4):
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

        data_store.append([cpc,route[1]])
        print(route)
    return route

def best_route(starting_location, intermediary_location, ending_location):
    return route(starting_location, intermediary_location) + route(intermediary_location, ending_location)[1:]

cpc_init=100
while(cpc_init>0):
    print('Route:')
    route('beg','end',cpc_init)
    cpc_init= cpc_init - 1

print(data_store)