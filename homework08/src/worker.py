import logging
import time
import json
from flask import Flask, request
import requests
from jobs import get_job_by_id, update_job_status, q, rd
import os
import redis

_redis_ip = os.environ.get('REDIS_IP','environment not found')
_redis_port = '6379'

res_db = redis.Redis(host=_redis_ip, port=6379, db=3)

# Read the log level from the environment variable
log_level = os.environ.get('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

def return_topics(para:dict):
    '''
    Function returns the major topics the catagory Cardiovascular Diseases (stroke, acute myocardial infarction, etc.).
    Args:
        para: input parameters (all functions in worker.py (other than do_work) have this as input). For this function, para can be anything, including an empty dictionary.
    Returns:
        classkeys: a list of strings, where each string is a cardiovascular disease.
    '''
    logger.info("Getting topics")
    classkeys = []
    for key in rd.keys():
        data = json.loads(rd.get(key))
        if data["category"] == 'Cardiovascular Diseases':
            if data["topic"] in classkeys:
                pass
            else:
                classkeys += [data["topic"]]
    logger.info("Returning topics")
    return classkeys

def return_year_data(para: dict):
    '''
    Function returns the data from the Redis database based on the specified year range.
    Args:
        para: input parameters containing 'start' and 'end' representing the year range.
    Returns:
        data_dict: a dictionary where keys are RowId and values are dictionaries containing the     data within the specified year range.
    '''
    logger.info("Getting year data")
    start_year = para['start']
    end_year = para['end']
    data_dict = {}
    index = 0
    for key in rd.keys():
        data = json.loads(rd.get(key))

        yr = data['year']
        if yr is not None and int(start_year) <= int(yr) <= int(end_year):
            data_dict[index] = data
            index+=1
    logger.info("Returning year data")
    return data_dict
"""
def max_affected(para:dict):
    keys_input = ["topic", "year", "gender"]
    keys_to_remove = []

    for spec in keys_input:
        logging.warning(f"spec = {spec}")
        if para[spec] == "":
            logging.warning(f"deleting one input para {spec}")
            keys_to_remove.append(spec)
        logging.warning(f"para['year'] {para['year']}")

    for key in keys_to_remove:
        keys_input.remove(key)



    count = 0
    for key in rd.keys():
        data = json.loads(rd.get(key))
 #       logging.warning("got one element of data")

        if data["category"] == 'Cardiovascular Diseases':
            correct_type = True
            for spec in keys_input:
#                logging.warning("why is it checking specs/years")
                if not(data[spec] == para[spec]):
                    correct_type = False
                    break

            if correct_type == True:
  #              logging.warning("has at least one of this type")

                if "data_value" in data.keys():
                    if count == 0:
                        maxpercent = data
                        count+=1
                        logging.warning(maxpercent)

                    if data["data_value"] >=maxpercent["data_value"]:
                        maxpercent = data

    try:
        x = maxpercent
    except:
        return "no data of this type can be found to analyze. /n"
    return maxpercent
"""

def max_affected(para: dict):
    keys_input = ["topic", "year", "gender"]
    keys_to_keep = [key for key in keys_input if para[key] != ""]

    maxpercent = None
    for key in rd.keys():
        data = json.loads(rd.get(key))
#        logging.warning(f"{data}")
        if data["category"] == 'Cardiovascular Diseases':
            correct_type = all(data[spec] == para[spec] for spec in keys_to_keep)

            if correct_type and "data_value" in data:
                if maxpercent is None or float(data["data_value"]) > float(maxpercent["data_value"]):
                    maxpercent = data
#                    logging.warning(f"max_percent={maxpercent}")
    if maxpercent is None:
        return "No data of this type can be found to analyze.\n"
    return maxpercent


def test_work(para:dict):
    '''
    This is a test function that simulatees work by sleeping for 20 seconds.
    Args:
        para: input parameters (all functions in worker.py (other than do_work) have this as input). For this function, para can be anything, including an empty dictionary.
    Returns:
        output: a dictionary of an example output
    '''
    logger.info("Starting test work")
    time.sleep(20)
    output = {"random output parameter 1": "1st output parameter value"}
    logger.info("Finished test work")
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
    logger.info(f"Starting job: {jobid}")
    update_job_status(jobid, 'in progress')
    job_desc = get_job_by_id(jobid)
    functName = job_desc["function_name"]
    input_para = job_desc["input_parameters"]

    output = eval(functName)(input_para)
    status = "complete"
    update_job_status(jobid, status)
    res_db.set(jobid, json.dumps(output))
    logger.info(f"Finished job: {jobid}")

if __name__ == '__main__':
    do_work()

































































