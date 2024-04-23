import logging
import time
import json
from flask import Flask, request
import requests
from jobs import get_job_by_id, update_job_status, q, rd
import os
import redis
from math import ceil
import matplotlib.pyplot as plt

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

def max_affected(para: dict):

    """
    Function returns the datum with the most percentage affected by the specified cardiovascular disease. 
    Args:
        para: input parameters dictionary. This can optionally contain the break_out type (an age category like 65+ or a gender like Male or a race like Hispanic), a location (like Arizona), and a specific cardiovascular disease (Stroke).
    Returns:
        the data dictionary with the maximum population percentage affected by the specified disease (if input) or a string that no data is found satisfying the specified inputs.
    """
    keys_input = ["topic", "year", "break_out"]
    keys_to_keep = [key for key in keys_input if para[key] != ""]

    maxpercent = None
    for key in rd.keys():
        data = json.loads(rd.get(key))
        if data["category"] == 'Cardiovascular Diseases':
            correct_type = all(data[spec] == para[spec] for spec in keys_to_keep)

            if correct_type and "data_value" in data:
                if maxpercent is None or float(data["data_value"]) > float(maxpercent["data_value"]):
                    maxpercent = data
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

def select_series(location:str, breakout:str, topic:str):
    '''
    Given a location, a topic, and breakout category, this function creates data for time vs data value series. Called on by rf_v_disease
    Args:
        para: input parameters. For this function parameters include breakout (str) (optional, default to overall), topic (str), lcoation (list)
    Returns:
        return_dict: The XY data for the graphs, X is the year, Y is the data value
    '''
    # What does return dict look like {X: Y}
    # loop through redis db, look for rd[key][location]
    # checks if the data value is between
    return_dict = {}
    for key in rd.keys():
        data = json.loads(rd.get(key))
        if data['data_value_typeid'] == 'Crude' and data['break_out_category'] != 'Age':
            continue
        if location == data['locationabbr'] or location == data['locationdesc']:
            if topic == data['topic'] and breakout == data['break_out']:
                # checks if data value is statistically relevant
                # if not, log warning with data value notes
                year = data['year']
                try:
                    data_value = data['data_value']
                except KeyError:
                    logger.warning(f"No data value for {location}, {year}, {topic}, {breakout}: {data['data_value_footnote']}")
                    continue
                return_dict[year] = data_value
            else:
                continue
        else:
            continue
    return return_dict

def graph_rf(para:dict):
    '''
    Given a location, a disease, a list of risk factors, and a breakout category, this function uses matplot lib to graph the disease and risk factor over time.
    Args:
        para (dict): This is a dictionary of parameters: 'breakout' (str) for break out (default to overall), 'disease' (str) for the disease, 'risk_factor' (list) for the list of risk factors, and 'location' (lst) for the location (default to USM)
    Outputs:
        ????
    '''
    location = para['location']
    risk_factors = para['risk_factors']
    disease = para['disease']
    # set the location default to USM
    if 'location' in para.keys():
        location = para['location']
    else:
        logger.warning(f"No paramerter was provided for location. Default to USM")
        location = 'USM'
    #set the breakout to Overall if it does not exist
    if 'breakout' in para.keys():
        breakout = para['breakout']
    else:
        logger.warning(f"No parameter was provided for breakout category")
        breakout = 'Overall'
    # for each location and topic, find the XY data
    cols = min(len(risk_factors), 3)
    rows = ceil(len(risk_factors)/3)
    figure, axis = plt.subplots(rows, cols)
    for risk_factor in risk_factors:
        # return {'disease' : select_series(location=location, topic=disease, breakout=breakout), 'rf': select_series(location=location, topic=risk_factor, breakout=breakout)}
        rf_data = select_series(location=location, topic=risk_factor, breakout=breakout)
        dis_data = select_series(location=location, topic=disease, breakout=breakout)
        
        # sort the data by the keys
        rf_sorted = {}
        for i in sorted(rf_data.keys()):
            rf_sorted[i] = rf_data[i]

        dis_sorted = {}
        for i in sorted(dis_data.keys()):
            dis_sorted[i] = dis_data[i]
        
        # plotting
        plt.scatter(dis_sorted.keys(), dis_sorted.values(), color = "r", label = f"{disease}")
        plt.scatter(rf_sorted.keys(), rf_sorted.values(), color = "b", label = f"{risk_factor}")
        plt.xlabel("Year")
        plt.ylabel(f"Prevalence amoung population (%)")
        plt.title(f"Age Standardized Rate of {disease.title()} and {risk_factor.title()} in {location} amoung {breakout} from {min(dis_data.keys())}-{max(dis_data.keys())}")
        plt.legend()
    
    # saving image to results db
    plt.savefig('/output_image.png', bbox_inches='tight')
    return

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
    # opening image and saving in redis
    if functName == 'graph_rf':
        with open('/output_image.png', 'rb') as f:
            img = f.read()
        res_db.set(jobid, img)
    else:
        res_db.set(jobid, json.dumps(output))
    status = "complete"
    update_job_status(jobid, status)
    logger.info(f"Finished job: {jobid}")

if __name__ == '__main__':
    do_work()
































































