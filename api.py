import requests
import redis
import json
import os
from flask import Flask, request
from jobs import add_job, get_job_by_id, get_all_job_ids, rd, delete_jobs

app = Flask(__name__)

@app.route('/jobs', methods=['GET'])
def all_jobs():
    """
    Function returns a list of all job ids.
    Args:
        None
    Returns:
        a list of all job ids (where the IDS are strings)
    """
    all_job_ids = get_all_job_ids()
    return all_job_ids

@app.route('/jobs/<functName>', methods=['POST'])
def submit_job(functName:str):
    """
    Function is used to submit jobs to the queue.
    Args:
        functName: an input function name argument (that will be called in the worker.py file)
    Returns:
        job_dict: a dictionary of the job information (the input parameters, function name, current status (submitted), etc.)
    """
    data = request.get_json()
    job_dict = add_job(functName, data)
    return job_dict

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

@app.route('/jobs/delete', methods = ["DELETE"])
def delete_all_jobs():
    """
    Function deletes all jobs in queue/not completed.
    Args:
       None.
    Returns:
       a string that all jobs have been deleted off of the queue.
    """
    delete_jobs()
    return "all jobs have been deleted off of worker queue. \n"

@app.route('/data', methods= ['GET', 'POST', 'DELETE'])
def edit_redis_data():
    """
    #Edits the redis database.
    #If method = POST, Posts the data into the redis data base
    #If method = GET, Returns all data in the db,
     #   Outputs: return_list (list), list of dictionaries containing all data in the db
    #if method = DELETE, Deletes all data from db
    """
    if request.method == 'POST':
        response = requests.get(url="https://data.cdc.gov/resource/ikwk-8git.json")
        data = response.json()
        for row in data:
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

#@app.route('/data', methods=['GET', 'POST', 'DELETE'])
#def edit_redis_data():
#    """
#    Function edits the redis database.
#    If method = POST, Posts the data into the redis data base
#    If method = GET, Returns all data in the db,
#        Outputs: return_list (list), list of dictionaries containing all data in the db
#    if method = DELETE, Deletes all data from db
#    Args:
#        None
#    Returns:
#        a successful data posted message (string): if post request
#        json formatted data: if get request
#        a successful data delted message (string): if delete request
#    """
#    if request.method == 'POST':
#        response = requests.get(url="https://data.cdc.gov/resource/ikwk-8git.json")
#        data = response.json()
#        for row in data:
#            # Adding the data to redis as a hash with the key being the row id
#            row_id = str(row['row_id'])
#            rd.set(row_id, json.dumps(row))
#        return "Data posted successfully\n"
#
#    if request.method == 'GET':
#        return_list = []
#        for key in rd.keys():
#            key_data = json.loads(rd.get(key))
#            return_list.append(key_data)
#        return json.dumps(return_list)
#
#    if request.method == 'DELETE':
#        rd.flushdb()
#        return "Data deleted successfully\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
