# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 09:55:16 2018

@author: legrandl
"""
import maths_tags

import certifi
import datetime
import json
import logging
import numpy as np
from openscoring import Openscoring
import paho.mqtt.client as mqtt
import pyodbc
import time
import urllib3
import urllib3.contrib.pyopenssl


def reset_data():
    global values_rupture
    global values_100
    global values_durete
    global values_allongement
    
    global n_rupture
    global n_100
    global n_durete
    global n_allongement
    
    values_rupture = {}
    values_100 = {}
    values_durete = {}
    values_allongement = {}
    
    n_rupture = -1
    n_100 = -1
    n_durete = -1
    n_allongement = -1
    
    print("RESET")
    logging.info("RESET")
    

def get_rheometer_data(lot):
    cursor_rheo.execute(query_rheo)
    
    MH = []
    ML = []
    
    rows = cursor_rheo.fetchall()
    for row in rows:
        if row[8] == lot:
            if row[0] == "ML":
                ML.append(float(row[1]))
            if row[0] == "MH":
                MH.append(float(row[1]))
    temp_dict = {'MH': ML, 'ML': ML}
    print(temp_dict)
    return temp_dict


def get_mixing_data():
    global last_update
    if time.time() - last_update > 10:
        last_update = time.time()
        
        global cursor_mes
        cursor_mes.execute(query_rheo2)
        row = cursor_mes.fetchone()
        global batch_consumed
        if batch_consumed != row[0]:
            batch_consumed = row[0]
            reset_data()
            temp_rheo = get_rheometer_data(batch_consumed)
            global data_rheo
            if temp_rheo['MH']:
                data_rheo = maths_tags.RHEO_Stags(temp_rheo['MH'], temp_rheo['ML'])
            else:
                data_rheo = {}

## Callback definition ##
def on_message_allongement(client, userdata, msg):
    global values_allongement
    global n_allongement
    n_allongement = n_allongement + 1
    
    temp = msg.payload.decode('utf-8')
    temp = temp.replace('\\', '/')
    json_temp = json.loads(temp)
    tags = {}
    tags['M_Caland_OpeningLevelLeft_SP'] = json_temp['values'][0]['v']
    tags['M_Caland_OpeningLevelRight_R'] = json_temp['values'][1]['v']
    tags['M_Cooler_Speed2_R'] = json_temp['values'][2]['v']
    
    values_allongement = maths_tags.Allgt_MESCO_Stags(tags, n_allongement, values_allongement)
    if data_rheo:
        values_allongement['MH_std'] = data_rheo['MH_std']
        values_allongement['MH_mean'] = data_rheo['MH_mean']
        result = os.evaluate("allongement", values_allongement)
        logging.info('Modele contrainte allongement : ' + str(result['probability(good)']))  
        print('Allongement : ' + str(result['probability(good)']))
        #send_to_visualization(result, tags, powerbi_allongement)
        
def on_message_durete(client, userdata, msg):
    global values_durete
    global n_durete
    n_durete = n_durete + 1

    temp = msg.payload.decode('utf-8')
    temp = temp.replace('\\', '/')
    json_temp = json.loads(temp)
    tags = {}
    tags['M_Caland_CylinderTemperatureLower_R'] = json_temp['values'][0]['v']
    tags['M_Caland_OpeningLevelLeft_R'] = json_temp['values'][1]['v']
    tags['M_Extrud_ScrewTemperature_R'] = json_temp['values'][2]['v']
    
    values_durete = maths_tags.Durete_MESCO_Stags(tags, n_durete, values_durete)
    if data_rheo:
        values_durete['MH_std'] = data_rheo['MH_std']
        values_durete['ML_std'] = data_rheo['ML_std']
    
        result = os.evaluate("durete", values_durete)
        logging.info('Modele contrainte durete : ' + str(result['probability(good)']))  
        print('Durete : ' + str(result['probability(good)']))
        #send_to_visualization(result, tags, powerbi_durete)
    else:
        print('No Mixing')

def on_message_rupture(client, userdata, msg):
    global values_rupture
    global n_rupture
    n_rupture = n_rupture + 1


    temp = msg.payload.decode('utf-8')
    temp = temp.replace('\\', '/')
    json_temp = json.loads(temp)
    tags = {}
    tags['M_Caland_OpeningLevelRight_R'] = json_temp['values'][0]['v']
    tags['M_Cooler_Speed2_R'] = json_temp['values'][3]['v']
    tags['M_Rotocure_CylinderTempLower_R'] = json_temp['values'][1]['v']
    tags['M_Rotocure_CylinderTempUpper_R'] = json_temp['values'][2]['v']
    tags['M_Rotocure_RotoCylinderTemp_R'] = json_temp['values'][4]['v']
    
    values_rupture = maths_tags.ModContRupt_SDtags(tags, n_rupture, values_rupture)
    
    tags['M_Caland_OpeningLevelRight_R_low'] = 0
    tags['M_Caland_OpeningLevelRight_R_high'] = 3
    
    result = os.evaluate("rupture", values_rupture)
    logging.info('Modele contrainte rupture : ' + str(result['probability(good)']))
    print('Rupture : ' + str(result['probability(good)']))
    send_to_visualization(result, tags, powerbi_rupture)
    get_mixing_data()
    print(batch_consumed)
    print(data_rheo)

    
def on_message_100(client, userdata, msg):
    global values_100
    global n_100
    n_100 = n_100 + 1
    
    temp = msg.payload.decode('utf-8')
    temp = temp.replace('\\', '/')
    json_temp = json.loads(temp)
    tags = {}
    tags['M_Caland_OpeningLevelLeft_R'] = json_temp['values'][0]['v']
    tags['M_Caland_OpeningLevelLeft_SP'] = json_temp['values'][1]['v']
    tags['M_Extrud_ScrewSpeed_SP'] = json_temp['values'][2]['v']
    tags['M_Extrud_MixtureTemperature_R'] = json_temp['values'][3]['v']
    tags['M_Extrud_HeadFlow_R'] = json_temp['values'][4]['v']
    
    values_100 = maths_tags.ModCont100_Stags(tags, n_100, values_100)
    
    result = os.evaluate("100", values_100)
    logging.info('Modele contrainte 100 : ' + str(result['probability(good)']))
    print('100 : ' + str(result['probability(good)']))
    send_to_visualization(result, tags, powerbi_100)
    
    
##############
def send_to_visualization(values, tags, powerbi):

    values['probability_good'] = values['probability(good)'] * 100
    values['probability_bad'] = values['probability(bad)'] * 100
    values['probability'] = values['_target']
    
    del values['probability(good)']
    del values['probability(bad)']
    del values['probability']
    
    values['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    values['probability_low'] = 0
    values['probability_high'] = 100
    
    data = {**values, **tags}
    json_temp = '[' + json.dumps(data) + ']'
    r = http.request('POST', powerbi, 
    headers={'Content-Type': 'application/json'},
    body=json_temp.encode('utf-8'))
    print(r.status)
    

###############################################################################
    
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))        

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("pmml/#")
    
## Default callback
def on_message(client, userdata, msg):
    pass

logging.basicConfig(filename='model.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.getLogger('requests').setLevel(logging.NOTSET)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

## Callback specification
client.message_callback_add("pmml/allongement", on_message_allongement)
client.message_callback_add("pmml/durete", on_message_durete)
client.message_callback_add("pmml/rupture", on_message_rupture)
client.message_callback_add("pmml/100", on_message_100)

## Openscoring definition and model deployment
os = Openscoring("http://localhost:8080/openscoring")

os.deployFile("rupture", "model/rank_contrainterupture.pmml")
os.deployFile("100", "model/rank_contrainte100.pmml")
os.deployFile("allongement", "model/rank_allongement.pmml")
os.deployFile("durete", "model/rank_durete.pmml")

## Global variable definition
urllib3.contrib.pyopenssl.inject_into_urllib3()
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

reset_data()

batch_consumed = ""

server_rheo = 'tcp:SLVDSQL02'
database_rheo = 'DJP_CTRL_RHEO'
username_rheo = 'DJP_CTRL_RHEO' 
password_rheo = 'AptarRheo2018'

cnxn_rheo = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server_rheo+';DATABASE='+database_rheo+';UID='+username_rheo+';PWD='+ password_rheo)
cursor_rheo = cnxn_rheo.cursor()
    
server_mes = 'tcp:SLVDDLK02'
database_mes = 'SLVDMES09_SUP3_VDR_PROD_ST'
username_mes = 'UP3READER' 
password_mes = 'up3reader'

cnxn_mes = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server_mes+';DATABASE='+database_mes+';UID='+username_mes+';PWD='+password_mes)
cursor_mes = cnxn_mes.cursor()

data_rheo = {}

last_update = time.time()

query_mes = """
select top 1 POI.order_item_name as OrdreDeFab
	from AT_OEE_STATE as ATOEE 
    join ORDERSTEP_UV as OS on ATOEE.work_order_step_114=OS.order_step_key 
	join CONTROL_RECIPE as CR on OS.control_recipe_key=CR.control_recipe_key
	join PROCESS_ORDER_ITEM as POI on cr.order_item_key=POI.order_item_key
where obj_name_S='V62002' and  ATOEE.work_order_step_114 is not null 
order by ATOEE.creation_time desc 
"""

query_rheo = """SET NOCOUNT ON;
    
DECLARE	@return_value int;
    
EXEC	@return_value = [dbo].[GetResultViewVariables]
		@testId = '1B9023AF-E0EF-11E7-B629-80000B71DFF8',
		@sampleTypeId = '638AC358-8B6F-4058-857D-83606A57F638',
		@numrows = 0,
		@numdays = 30;
"""

## Code machine LVC2 : 28637 LVC3 : 28655
query_rheo2 = """
select top 1 batch_name_S, creation_time 
from AT_BOX_CONSUMPTION_INFO 
where equipment_12=28637 
order by creation_time desc
"""

powerbi_rupture = "https://api.powerbi.com/beta/5fd74a3e-d57a-410e-8d7c-02c4df062234/datasets/3834d12f-8f3e-47fe-a835-93cd5dce9bc7/rows?key=yqYZq%2BqylrK5y4yIzk8IPcb4yGAl2%2FMWGw5wzaebMaTItGQW%2FbxeLETD61ffHdApDKp7HLOYQIh%2BjIVpXqHN7Q%3D%3D"
powerbi_100 = "https://api.powerbi.com/beta/5fd74a3e-d57a-410e-8d7c-02c4df062234/datasets/50a264cb-a122-4f74-8399-cf85308fe355/rows?key=D8dDNZnRnfhmC4vnOK3z8GQw3eBjLrFdOxMzXVkmPNvQSWQIo9X5d7SO5DS2woNdFJx76aM8ddmb%2BAEmzpo0Mg%3D%3D"

## Connection
client.connect("slvdup301", 1883, 60)
        
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

print('hello')



##################################################################################
##################################################################################
##################################################################################


# =============================================================================TRUE FUNCTION
# def on_message_rupture(client, userdata, msg):
#     global values_rupture
#     global n_rupture
#     n_rupture = n_rupture + 1
# 
# 
#     temp = msg.payload.decode('utf-8')
#     temp = temp.replace('\\', '/')
#     json_temp = json.loads(temp)
#     tags = {}
#     tags['M_Caland_OpeningLevelRight_R'] = json_temp['values'][0]['v']
#     tags['M_Cooler_Speed2_R'] = json_temp['values'][1]['v']
#     tags['M_Rotocure_CylinderTempLower_R'] = json_temp['values'][2]['v']
#     tags['M_Rotocure_CylinderTempUpper_R'] = json_temp['values'][3]['v']
#     tags['M_Rotocure_RotoCylinderTemp_R'] = json_temp['values'][4]['v']
#     
#     values_rupture = maths_tags.ModContRupt_SDtags(tags, n_rupture, values_rupture)
#     
#     tags['M_Caland_OpeningLevelRight_R_low'] = 0
#     tags['M_Caland_OpeningLevelRight_R_high'] = 3
#     
#     result = os.evaluate("rupture", values_rupture)
#     logging.info('Modele contrainte rupture : ' + str(result['probability(good)']))
#     send_to_visualization(result, tags, powerbi_rupture)
#     get_mixing_data()
#     print(batch_consumed)
#     print(data_rheo)
#     
# =============================================================================
