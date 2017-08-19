"""
flaskr.py

Demo:
. env.bash
$PYTHON flaskr.py
Other shell:
curl localhost:5011/demo11.json
curl localhost:5011/static/hello.json
curl localhost:5011/tkrlist
curl localhost:5011/istkr/IBM
curl localhost:5011/years
curl localhost:5011/tkrprices/SNAP
curl localhost:5011/sklinear/ABC/20/2016-12/'pct_lag1,slope3,dow,moy'
curl localhost:5011/keras_linear/ABC/20/2016-12/'pct_lag2,slope5,dow,moy'
curl localhost:5011/keras_nn/IBM/25/2014-11?features='pctlag1,slope4,moy'&hl=2&neurons=4
curl localhost:5011/sklinear_yr/IBM/20/2016/'pct_lag1,slope3,dow,moy'
curl localhost:5011/keraslinear_yr/IBM/20/2016/'pct_lag1,slope3,dow,moy'
"""

import io
import pdb
import os
import datetime      as dt
import flask         as fl
import flask_restful as fr
import numpy         as np
import pandas        as pd
import sqlalchemy    as sql
import sklearn.linear_model as skl
# modules in the py folder:
import pgdb
import sktkr
import kerastkr

# I should connect to the DB
db_s = os.environ['PGURL']
conn = sql.create_engine(db_s).connect()

# I should ready flask_restful:
application = fl.Flask(__name__)
api         = fr.Api(application)

# I should fill lists which users want frequently:
with open('years.txt') as fh:
  years_l = fh.read().split()
  
with open('tkrlist.txt') as fh:
  tkrlist_l = fh.read().split()
  
class Demo11(fr.Resource):
  """
  This class should be a simple syntax demo.
  """
  def get(self):
    my_k_s = 'hello'
    my_v_s = 'world'
    return {my_k_s: my_v_s}
api.add_resource(Demo11, '/demo11.json')

class Tkrlist(fr.Resource):
  """
  This class should list all the tkrs in tkrlist.txt
  """
  def get(self):
    return {'tkrlist': tkrlist_l}
api.add_resource(Tkrlist, '/tkrlist')

class Istkr(fr.Resource):
  """
  This class should answer True, False given a tkr.
  """
  def get(self, tkr):
    torf = tkr in tkrlist_l
    return {'istkr': torf}
api.add_resource(Istkr, '/istkr/<tkr>')

class Years(fr.Resource):
  """
  This class should list all the years in years.txt
  """
  def get(self):
    return {'years': years_l}
api.add_resource(Years, '/years')

class Tkrprices(fr.Resource):
  """
  This class should list prices for a tkr.
  """
  def get(self, tkr):
    # I should get csvh from tkrprices in db:
    sql_s       = '''select csvh from tkrprices
      where tkr = %s  LIMIT 1'''
    result      = conn.execute(sql_s,[tkr])
    if not result.rowcount:
      return {'no': 'data found'}  
    myrow       = [row for row in result][0]
    return {'tkrprices': myrow.csvh.split()}
api.add_resource(Tkrprices, '/tkrprices/<tkr>')

def get_out_d(out_df):
  """This function should convert out_df to a readable format when in JSON."""
  out_l = []
  for row in out_df.itertuples():
    row_d       = {
      'date,price':[row.cdate,row.cp]
      ,'pct_lead': row.pct_lead
      ,'prediction,effectiveness,accuracy':[row.prediction,row.effectiveness,row.accuracy]
    }
    out_l.append(row_d)
    lo_acc = sum((1+np.sign(out_df.pct_lead))/2) / out_df.accuracy.size
    out_d  = {'Long-Only-Accuracy': lo_acc }
    out_d['Long-Only-Effectivness'] = sum(out_df.pct_lead)
    out_d['Model-Effectivness']     = sum(out_df.effectiveness)
    out_d['Model-Accuracy']         = sum(out_df.accuracy) / out_df.accuracy.size
    out_d['Prediction-Count']       = out_df.prediction.size
    out_d['Prediction-Details']     = out_l
  return out_d

class Sklinear(fr.Resource):
  """
  This class should return predictions from sklearn.
  """
  def get(self, tkr,yrs,mnth,features):
    out_df = sktkr.learn_predict_sklinear(tkr,yrs,mnth,features)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(Sklinear, '/sklinear/<tkr>/<int:yrs>/<mnth>/<features>')

class KerasLinear(fr.Resource):
  """
  This class should return predictions from keras.
  """
  def get(self, tkr,yrs,mnth,features):
    out_df = kerastkr.learn_predict_keraslinear(tkr,yrs,mnth,features)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KerasLinear, '/keras_linear/<tkr>/<int:yrs>/<mnth>/<features>')
  
class KerasNN(fr.Resource):
  """
  This class should return predictions from keras.
  """
  def get(self, tkr,yrs,mnth):
    features_s = fl.request.args.get('features', 'pctlag1,slope3,dom')
    hl_s       = fl.request.args.get('hl', '2')      # default 2
    neurons_s  = fl.request.args.get('neurons', '4') # default 4
    hl_i       = int(hl_s)
    neurons_i  = int(neurons_s)
    out_df = kerastkr.learn_predict_kerasnn(tkr,yrs,mnth,features_s,hl_i,neurons_i)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KerasNN, '/keras_nn/<tkr>/<int:yrs>/<mnth>')

class SklinearYr(fr.Resource):
  """
  This class should return predictions from sklearn for a Year.
  """
  def get(self, tkr,yrs,yr,features):
    out_df = sktkr.learn_predict_sklinear_yr(tkr,yrs,yr,features)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(SklinearYr, '/sklinear_yr/<tkr>/<int:yrs>/<int:yr>/<features>')

class KeraslinearYr(fr.Resource):
  """
  This class should return predictions from sklearn for a Year.
  """
  def get(self, tkr,yrs,yr,features):
    out_df = kerastkr.learn_predict_keraslinear_yr(tkr,yrs,yr,features)
    out_d  = get_out_d(out_df)
    return {'predictions': out_d}
api.add_resource(KeraslinearYr, '/keraslinear_yr/<tkr>/<int:yrs>/<int:yr>/<features>')
  
if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  application.run(host='0.0.0.0', port=port)
'bye'
