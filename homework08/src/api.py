import logging
import requests
import redis
import json
import os
from flask import Flask, request, jsonify
from jobs import add_job, get_job_by_id, get_all_job_ids, rd, delete_jobs, jdb
from worker import res_db
#from jobs import res_db

app = Flask(__name__)



# Read the log level from the environment variable
log_level = os.environ.get('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


@app.route('/jobs', methods=['GET'])
def all_jobs():
    """
    Function returns a list of all job ids.
    Args:
        None
    Returns:
        a list of all job ids (where the IDS are strings)
    """
    logger.info("Received GET request for all jobs.")
    all_job_ids = get_all_job_ids()
    return all_job_ids

"""
def validate_year(data):
   
    if "start" not in data or "end" not in data:
        return False
    try:
        start = int(data["start"])
        end = int(data["end"])
    except:
        logger.warning(f"Correct input parameters not submitted by user for '{functName}'.")
        return False
    return True
"""


@app.route('/<functName>', methods=['POST'])
def submit_job(functName:str):
    """
    Function is used to submit jobs to the queue.
    Args:
        functName: an input function name argument (that will be called in the worker.py file)
    Returns:
        job_dict: a dictionary of the job information (the input parameters, function name, current status (submitted), etc.)
    """
    logger.info(f"Received POST request for job '{functName}'.")
    worker_functs = ["return_topics","test_work","max_affected"]
    if not(functName in worker_functs):
         return jsonify({"error": "Invalid function name."}), 400
    should_continue = True
    data = request.get_json()
     
    if functName == "return_topics":
        data = {} # no data needed

    elif functName == "test_work":
        data = {}
"""        
    elif functName == "return_year_data":
        try:
            x = int(data["start"])
            y = int(data["end"])
        except:
            should_continue = False
            return jsonify({"error": "Invalid input. Please provide 'start' and 'end' as strings of integers. For example {'start':'1999','end':'2000'}"}), 400
"""

    elif functName == "max_affected":

        paras = ["topic", "year","break_out"]
        for elem in paras:
            try:
                x = data[elem]
            except:
                data[elem] = ""

        # Add job to the queue
    if should_continue:
        job_dict = add_job(functName, data)
        return job_dict

#@app.route('/jobs/<jid>', methods=['GET'])
def get_job_by_id(jid:str):
    """
    Function return job dictionary (with status and, possibly, an output) given jid.
    Args:
        jid: job id of job in queue.
    Returns:
        a dictionary of the job information (with the status, output, function name, input \
parameters, etc.)
        OR:
        an dictionary with an error message, if the job id does not exist
    """
    """
    result = res_db.get(jid)
    if result is not None:
        return json.loads(result)
    else:
        return {"error": "result not found"}
    """
    logger.info(f"Received GET request for job '{jid}'.")
    job_dict = jdb.get(jid)
    if job_dict is not None:
        return json.loads(job_dict)
    else:
        logger.info(f"No job found by {jid} id, did user input correct ID? recheck with /jobs route for all valid job ids")
        return {"error":"job not found"}  # Return an empty dictionary if job not found



@app.route('/jobs/<jobid>', methods=['GET'])
def get_job(jobid:str):
    """
    Function returns the status/output of the job.
    Args:
       jobid: the job's id, a string
    Returns:
       result: the dictionary of the job information (the job id, status, output, functName, etc.)
       OR:
       returns an error message (string) that job was never placed on queue or cannot be found.
    """
    result = get_job_by_id(jobid)
    if result == "error":
        return "job does not exist (never was placed on queue) or has been deleted. \n"
    return result


def get_result_by_id(jid:str):
    result = res_db.get(jid)
    if result is not None:
        return json.loads(result)
    else:
        return {"error": "result not found"}

@app.route('/results/<jobid>', methods=['GET'])
def get_result(jobid:str):
    """
    Function checks if a result has been posted for a specific job id, then returns that result (if it exists). Otherwise, it returns an error message.
    Args:
        jobid (str): the job id, a string
    Returns:
        result: the job output (if successfuly complted) in a json format.
        Or:
        returns an error message in json format
    """
    result = get_result_by_id(jobid)
    if result == {"error": "result not found"}:
        return "Result not found for the specified Job ID. Check completion status of job. \n"
    return jsonify(result)



@app.route('/jobs/delete', methods = ["DELETE"])
def delete_all_jobs():
    """
    Function deletes all jobs in queue/not completed.
    Args:
       None.
    Returns:
       a string that all jobs have been deleted off of the queue.
    """
    logger.warning("Received DELETE request to delete all jobs.")
    delete_jobs()
    return "all jobs have been deleted off of worker queue. \n"

@app.route('/data', methods= ['GET', 'POST', 'DELETE'])
def edit_redis_data():
    """
    Edits the redis database.
    If method = POST, Posts the data into the redis data base
    If method = GET, Returns all data in the db,
        Outputs: return_list (list), list of dictionaries containing all da    keys_input = ["topic", "year", "gender", "a"]
    keys_to_remove = []

    for spec in keys_input:
        logging.warning(f"spec = {spec}")
        if para[spec] == "":
            logging.warning(f"deleting one input para {spec}")
            keys_to_remove.append(spec)
        logging.warning(f"para['year'] {para['year']}")

    for key in keys_to_remove:
        keys_input.remove(key)

    return keys_inputta in the db
    if method = DELETE, Deletes all data from db
    Args:
        None
    Returns:
        str : message about data being posted or deleted from redis
        OR
        list: of all dictionary data
    """
    if request.method == 'POST':

        url = "https://data.cdc.gov/resource/ikwk-8git.json"
        limit = 1000  # Number of records to fetch per request
        offset = 0  # Initial offset

        all_data = []  # List to store all data

        while True:
            response = requests.get(url=url, params={"$limit": limit, "$offset": offset})
            data = response.json()
            if not data:  # If no more data is returned, break the loop
                break
            all_data.extend(data)  # Append the data to the list
            offset += limit  # Increment the offset for the next request

#        all_data_json = json.dumps(all_data)  # Serialize the list to a JSON string


        for row in all_data:
    # Adding the data to redis as a hash with teh key being teh row id
            row_id = str(row['row_id'])
            rd.set(row_id, json.dumps(row))
        return "Data posted successfully\n"

    if request.method == 'GET':
        return_list = []
        for key in rd.keys():
            key_data = json.loads(rd.get(key))
            return_list.append(key_data)
        return return_list
    if request.method == 'DELETE':
        rd.flushdb()
        return "Data deleted successfully\n"


@app.route('/year_data', methods=['GET'])
def return_year_data():
    '''
    Function returns the data from the Redis database based on the specified year range.
    Args:
        start_year (int): The start year of the range.
        end_year (int): The end year of the range.
    Returns:
        data_dict: A dictionary where keys are RowId and values are dictionaries containing the data within the specified year range.
    '''
    try:
        start_year = int(request.args.get('start'))
    except:
        start_year = 0
    try:
        end_year = int(request.args.get('end'))
    except:
        end_year = 5000
    logger.info("Getting year data")
    data_dict = {}
    index = 0
    for key in rd.keys():
        data = json.loads(rd.get(key))
        yr = data.get('year')
        if yr is not None and start_year <= int(yr) <= end_year:
            data_dict[index] = data
            index += 1
    logger.info("Returning year data")
    return jsonify(data_dict)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)











