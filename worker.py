import time
import json  
from flask import Flask, request
import requests 
from jobs import get_job_by_id, update_job_status, q, rd

def return_topics(para:dict):
    '''
    Function returns the major topics the catagory Cardiovascular Diseases (stroke, acute myocardial infarction, etc.).
    Args:
        para: input parameters (all functions in worker.py (other than do_work) have this as input). For this function, para can be anything, including an empty dictionary.
    Returns:
        classkeys: a list of strings, where each string is a cardiovascular disease.
    '''
    classkeys = []
    for key in rd.keys():
        data = json.loads(rd.get(key))
        if data["category"] == 'Cardiovascular Diseases':
            if data["topic"] in classkeys:
                pass
            else:
                classkeys += [data["topic"]]
    return classkeys

def test_work(para:dict):
    '''
    This is a test function that simulatees work by sleeping for 20 seconds. 
    Args:
        para: input parameters (all functions in worker.py (other than do_work) have this as input). For this function, para can be anything, including an empty dictionary.
    Returns:
        output: a dictionary of an example output
    '''
    time.sleep(20)
    output = {"random output parameter 1": "1st output parameter value"}
    return output

@q.worker
def do_work(jobid:str):
    '''
    Main function in worker.py. It calls different worker functions (each of which provides a certain type of analysis). 
    Args:
        jobid: a string, which is the jobid of the particular job in the queue
    Returns:
        None: the function updates the job with the output data, and when users curl a get route, that information is displayed to the screen. 
    '''
    update_job_status(jobid, 'in progress')
    job_desc = get_job_by_id(jobid)
    functName = job_desc["function_name"]
    input_para = job_desc["input_parameters"]
    
    output = eval(functName)(input_para)
    status = "complete"
    update_job_status(jobid, status, output)

if __name__ == '__main__':
    do_work()

