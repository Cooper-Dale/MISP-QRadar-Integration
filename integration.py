# usage: python3 MISP-QRADAR-integration.py >> /home/misp/misp-integration.log &
# credits: https://github.com/karthikkbala/MISP-QRadar-Integration

import requests
import json
import sys
import time
import re
import socket
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#------*****------#

misp_auth_key = "YTcGLT6K2WC2DCbWemvYzeKBgc7ZzcxCOSnD"
qradar_auth_key = "535f1adf-04b6-479c7c-7d093c3a07fe"
qradar_ref_set = "MISP_Event_IOC"
misp_server = "x"
qradar_server = "y"
#frequency = 60 # In minutes
frequency = 15

#------*****------#

#misp_url = "https://" + misp_server + "/attributes/restSearch/json/null/"
misp_url = "http://" + misp_server + "/attributes/restSearch/json/null/"

QRadar_POST_url = "https://" + qradar_server + "/api/reference_data/sets/bulk_load/" + qradar_ref_set

MISP_headers = {
    'authorization': misp_auth_key,
    'cache-control': "no-cache",
    }

QRadar_headers = {
    'sec': qradar_auth_key,
    'content-type': "application/json",
    }

def validate_refSet():
    validate_refSet_url = "https://" + qradar_server + "/api/reference_data/sets/" + qradar_ref_set
    validate_response = requests.request("GET", validate_refSet_url, headers=QRadar_headers, verify=False)
    print (time.strftime("%H:%M:%S") + " -- " + "Validating if reference set " + qradar_ref_set + " exists")
    if validate_response.status_code == 200:
        print(time.strftime("%H:%M:%S") + " -- " + "Validating reference set " + qradar_ref_set + " - (Success) ")
        validate_response_data = validate_response.json()
        refSet_etype = (validate_response_data["element_type"])
        print(time.strftime("%H:%M:%S") + " -- " + "Identifying Reference set " + qradar_ref_set + " element type")
        print(time.strftime("%H:%M:%S") + " -- " + "Reference set element type = " + refSet_etype + " (Success) ")
        if refSet_etype == "IP":
            print (time.strftime("%H:%M:%S") + " -- " + "The QRadar Reference Set " + qradar_ref_set + " Element Type = \"IP\". Only IPs will be imported to QRadar and the other IOC types will be discarded")
            get_misp_data(refSet_etype)
        else:
            get_misp_data(refSet_etype)
    else:
        print(time.strftime("%H:%M:%S") + " -- " + "QRadar Reference Set does not exist, please verify if reference set exists in QRadar.")
        sys.exit()

def get_misp_data(refSet_etype):
    print(time.strftime("%H:%M:%S") + " -- " + "Initiating, GET data from MISP on " + misp_server)
    misp_response = requests.request('GET', misp_url, headers=MISP_headers, verify=False)
    json_data = misp_response.json()
    ioc_list = []
    if misp_response.status_code == 200:
        print(time.strftime("%H:%M:%S") + " -- " + "MISP API Query (Success) ")
        for data in json_data["response"]["Attribute"]:
            iocs = (data['value'])
            ioc_list.append(iocs)
        import_data = json.dumps(ioc_list)
        ioc_count = len(ioc_list)
        print(time.strftime("%H:%M:%S") + " -- " + str(ioc_count) + " IOCs imported")
        if refSet_etype == "IP":
            print(time.strftime("%H:%M:%S") + " -- " + "Trying to clean the IOCs to IP address, as " + qradar_ref_set + " element type = IP")
            # IPv6???
            # r = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
            r = re.compile("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
            ioc_cleaned = list(filter(r.match, ioc_list))
            ioc_cleaned_data = json.dumps(ioc_cleaned)
            ioc_count_cleaned = len(ioc_cleaned)
            print(time.strftime("%H:%M:%S") + " -- " + "(Success) Extracted " + str(ioc_count_cleaned) + " IPs from initial import.")
            qradar_post_IP(ioc_cleaned_data, ioc_count_cleaned)
        else:
            qradar_post_all(import_data, ioc_count)
    else:
        print(time.strftime("%H:%M:%S") + " -- " + "MISP API Query (Failed), Please check the network connectivity")
        sys.exit()

def qradar_post_IP(ioc_cleaned_data, ioc_count_cleaned):
# curl -s -X POST -u Cooper -H 'Content-Type: application/json' -H 'Version: 9.1' -H 'Accept: application/json' --data-binary '["1.1.1.1","2.2.2.3"]' 'https://qradar.bb.iwy/api/reference_data/sets/bulk_load/MISP-test_Event_IOC'
    print(time.strftime("%H:%M:%S") + " -- " + "Initiating, IOC POST to QRadar ")
    qradar_response = requests.request("POST", QRadar_POST_url, data=ioc_cleaned_data, headers=QRadar_headers, verify=False)
    if qradar_response.status_code == 200:
        print(time.strftime("%H:%M:%S") + " -- " + "Imported " + str(ioc_count_cleaned) + " IOCs to QRadar (Success)" )
    else:
        print(time.strftime("%H:%M:%S") + " -- " + "Could not POST IOCs to QRadar (IP) (Failure). HTTP Status code: " + str(qradar_response.status_code) + "." )

def qradar_post_all(import_data, ioc_count):
    print(time.strftime("%H:%M:%S") + " -- " + "Initiating, IOC POST to QRadar ")
    qradar_response = requests.request("POST", QRadar_POST_url, data=import_data, headers=QRadar_headers, verify=False)
    if qradar_response.status_code == 200:
        print(time.strftime("%H:%M:%S") + " -- " + " (Finished) Imported " + str(ioc_count) + " IOCs to QRadar (Success)" )
        print(time.strftime("%H:%M:%S") + " -- " + "Waiting to next schedule in " + schedule + "minutes")
    else:
        print(time.strftime("%H:%M:%S") + " -- " + "Could not POST IOCs to QRadar (all) (Failure)")

def socket_check_qradar():
    print(time.strftime("%H:%M:%S") + " -- " + "Checking HTTPS Connectivity to QRadar")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((qradar_server, int(443)))
    if result == 0:
        print(time.strftime("%H:%M:%S") + " -- " + "(Success) HTTPS Connectivity to QRadar")
        socket_check_misp()
    else:
        print(time.strftime("%H:%M:%S") + " -- " + "Could not establish HTTPS connection to QRadar, Please check connectivity before proceeding.")

def socket_check_misp():
    print(time.strftime("%H:%M:%S") + " -- " + "Checking HTTPS Connectivity to MISP")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((misp_server, int(443)))
    if result == 0:
        print(time.strftime("%H:%M:%S") + " -- " + "(Success) HTTPS Connectivity to MISP")
        validate_refSet()
    else:
        print(time.strftime("%H:%M:%S") + " -- " + "Could not establish HTTPS connection to MISP Server, Please check connectivity before proceeding.")

scheduler = BlockingScheduler()
scheduler.add_job(socket_check_qradar, 'interval', minutes=frequency, next_run_time=datetime.datetime.now())
scheduler.start()
