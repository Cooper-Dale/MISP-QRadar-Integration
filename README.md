# QRadar MISP Integration
Integrate QRadar with IOC (Attributes) from MISP - Open Source Threat Intelligence Platform

### IBM QRadar:
 
![alt text](https://www.threatconnect.com/wp-content/uploads/QRadar-logo-Website.png "IBM QRadar")

IBM QRadar Security Information and Event Management (SIEM) centrally collects and analyzes log and network flow data throughout even the most highly distributed environments to provide actionable insights into threats.

Using advanced analytics, the solution automatically sorts through millions to billions of events per day to detect anomalous and malicious activities, identify and group related events, and generate prioritized alerts to only the most critical threats.

### MISP:

![alt text](https://raw.githubusercontent.com/MISP/MISP/2.4/INSTALL/logos/misp-logo.png "MISP")

The MISP threat sharing platform is a free and open source software helping information sharing of threat intelligence including cyber security indicators.

MISP is a threat intelligence platform for gathering, sharing, storing and correlating Indicators of Compromise of targeted attacks, threat intelligence, financial fraud information, vulnerability information or even counter-terrorism information.

Many organizations use MISP to maintain internal repository of IOCs involved in any security incident of the organization.

MISP has rich RESTful API support to integrate with any producers or consumers of threat intelligence information.

### Requirements:

 - Linux
 - Python 3 
 - apscheduler
 - PyMISP
 
### Installation:
```sh
git clone https://github.com/Cooper-Dale/MISP-QRadar-Integration.git
```

### Configuration:

Edit the integration.py file with favourite editor and provide the following information.

```sh
misp_auth_key = "mxVt2yZWkS39XemrgtyhbfYts7ZeeheQ50dXKLHO"
qradar_auth_key = "811aacf9-ef79-456h-98d4-5d27b7a94844"
qradar_ref_set = "MISP_Event_IOC"
MISP_body = '{"limit":"10","to_ids":"true","type":"ip-dst", ....}'
misp_server = "IP Address of MISP Server"
qradar_server = "IP Address of QRadar Server"
frequency = 60 # In minutes
```

### Usage:
```sh
python3 integration.py >> /var/log/misp-integration.log &
```

### Error Handling - Use Cases
 - Validate if the reference set exists
 - Identify the Element Type of the reference set
 - If the Reference Set - Element Type is IP, only the IPs from the MISP will be imported to Reference Set.
 - Socket connection validation for QRadar and MISP
 - Validate body/filter settings

### Output - Success

```
13:26:52 -- Checking HTTPS Connectivity to QRadar
13:26:52 -- (Success) HTTPS Connectivity to QRadar
13:26:52 -- Checking HTTPS Connectivity to MISP
13:26:52 -- (Success) HTTPS Connectivity to MISP
13:26:53 -- Validating if reference set MISP-test_Event_IOC exists
13:26:53 -- Validating reference set MISP-test_Event_IOC - (Success)
13:26:53 -- Identifying Reference set MISP-test_Event_IOC element type
13:26:53 -- Reference set element type = IP (Success)
13:26:53 -- The QRadar Reference Set MISP-test_Event_IOC Element Type = "IP". Only IPs will be imported to QRadar and the other IOC types will be discarded
13:26:53 -- Filter:  {"limit":"10","to_ids":"true","type":"ip-dst"}
13:26:53 -- Initiating, GET data from MISP on x.x.x.x
13:26:53 -- MISP API Query (Success)
13:26:53 -- 10 IOCs imported
13:26:53 -- Trying to clean the IOCs to IP address, as MISP-test_Event_IOC element type = IP
13:26:53 -- (Success) Extracted 10 IPs from initial import.
13:26:53 -- Initiating, IOC POST to QRadar
13:26:53 -- Imported 10 IOCs to QRadar (Success)

```
