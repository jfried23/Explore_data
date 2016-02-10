import os, io
import flask
import simplejson
import numpy as np
import math
import pandas as pd


app = flask.Flask( __name__ )



def calc_time_to_visit( df, race, cut = 5,):
    """
    This calculates the average rate of premature birth 'prem_birth_rate_by_state'
    and the average month of pregancy in which healthcare began for each state.
    """
    a=df
    a= a[ a['month_care_began'] < 10 ]
    if race !=4: a=a[ a['Race'] == race ]

    a['premature'] = a['Gestational_Age'] < cut

    totl_state_births = a.groupby('State').agg({'num_births':np.sum})
    prem_birth_rate_by_state = 100*a[a.premature==True].groupby(['State']).agg({'num_births':np.sum})/totl_state_births

    prem_birth_rate_by_state = prem_birth_rate_by_state.num_births

    n = a.groupby(['State','month_care_began']).agg({'num_births':np.sum}).reset_index()
    n['tmp']= n['month_care_began']*n['num_births']
    total_coh_births = n.groupby('State').agg({'num_births':np.sum})
    tmp = n.groupby('State').agg({'tmp':np.sum})
    avg_care_began = tmp.values/total_coh_births.values

    return avg_care_began.flatten().tolist(), prem_birth_rate_by_state.values.tolist(), tmp.index.tolist(), tmp['tmp'].values.tolist()



@app.route('/index', methods=['POST','GET'])
def run_index():

  if flask.request.method == 'GET':

    df = pd.read_csv('./static/cleaned.csv')

    to_pass =[]

    x,y,s, r= calc_time_to_visit(df, race=4)
    for i,v in enumerate( x ):
      if math.isnan(y[i]): continue

      to_pass.append({'x':x[i],'y':y[i],'id':4, 's':s[i], 'r':r[i]})


    return flask.render_template( 'index.html', data=simplejson.dumps(to_pass)  )

  elif flask.request.method == 'POST':
    eth_id =  flask.request.form.getlist('eth_id')
    cutoff =  flask.request.form['months']
    df = pd.read_csv('./static/cleaned.csv')

    to_pass =[]


    for e in eth_id:
      x,y,s, r= calc_time_to_visit(df, race=int(e), cut=int(cutoff))
      for i,v in enumerate( x ):
        if math.isnan(y[i]): continue
        to_pass.append({'x':x[i],'y':y[i],'id':e, 's':s[i], 'r':r[i]})

    return flask.render_template( 'index.html', data=simplejson.dumps(to_pass)  )



if __name__ == '__main__':

  #port = int(os.environ.get("PORT", 5000))
  #app.run(host='0.0.0.0', port=port)

  app.run( debug=True )
