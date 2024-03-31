import time
import json  # Add this import
from flask import Flask, request
import requests 
from jobs import get_job_by_id, update_job_status, q, rd

def cardio_data():
    response = requests.get("https://data.cdc.gov/resource/ikwk-8git.json")
    data = response.json()
    return data

def return_classes(para):
    data = cardio_data()
    classkeys = []
    for line in data:
        if line["category"] == 'Cardiovascular Diseases':
            if line["topic"] in classkeys:
                pass
            else:
                classkeys += [line["topic"]]
        else:
            break
    return classkeys

def test_work(para):
    time.sleep(20)
    output = {"random output parameter 1": "1st output parameter value"}
    return output

@q.worker
def do_work(jobid):
    update_job_status(jobid, 'in progress')
    job_desc = get_job_by_id(jobid)
    functName = job_desc["function_name"]
    
    input_para = job_desc["input_parameters"]
    
    output = eval(functName)(input_para)
    status = "complete"
    update_job_status(jobid, status, output)

if __name__ == '__main__':
    do_work()

