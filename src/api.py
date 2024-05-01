import logging
import requests
import redis
import json
import os
from flask import Flask, request, jsonify, send_file
from jobs import add_job, get_job_by_id, get_all_job_ids, rd, delete_jobs, jdb
from worker import res_db
#from jobs import res_db

app = Flask(__name__)



# Read the log level from the environment variable
log_level = os.environ.get('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def help()->str:
    """
    Helper function to return possible functions/jobs in this app.
    Args:
        None
    Returns:
        route_info: a string of different functions/jobs.
    """
    route_info = """
- Route: `/`
\t- Purpose: Help route. Returns all the possible functions/commands users can use (this image).
\t- Example:
\t\t- Internet: `cardio-app.coe332.tacc.cloud/`
\t\t- Local laptop: `curl cardio-app.coe332.tacc.cloud/`

- Route: `/data`
\t- Purpose: GET, POST, or DELETE data from Redis. Replace command (`-X GET`) with appropriate/desired flag (`-X POST` to post data to Redis).
\t- Example:
\t\t- Internet: `cardio-app.coe332.tacc.cloud/data`
\t\t- Local laptop: `curl cardio-app.coe332.tacc.cloud/data`

- Route: `/year_data?start=int&end=int`
\t- Purpose: Returns data from Redis within the user-specified range (start is the earliest data to be returned while end is the last year of data that is returned. Note that start and end are optional parameters. Also note the quotes (required when users input more than one query argument).
\t- Example:
\t\t- Internet: `cardio-app.coe332.tacc.cloud/year_data?start=2018&end=2020`
\t\t- Local laptop: `curl “cardio-app.coe332.tacc.cloud/year_data?start=2018&end=2020”`

- Route: `/jobs`
\t- Purpose: GET route returns all jobs that have been completed, in-progress, or have been submitted; returns a list of job ids(unique identifiers for each job).
\t- Example:
\t\t- Local laptop: `curl cardio-app.coe332.tacc.cloud/jobs -X GET`

- Route: `/jobs/return_topics`
\t- Purpose: POST route posts a job to the queue. There are 3 different jobs: return_topics, max_affected, and XXX.
\t- Example:
\t\t- Local laptop: `curl cardio-app.coe332.tacc.cloud/jobs/return_topics -X POST -d '{}' -H "Content-Type: application/json"`

- Route: `/jobs/max_affected`
\t- Purpose: POST route posts a job to the queue. There are 3 different jobs: return_topics, max_affected, and XXX.
\t- Example:
\t\t- Local laptop: `curl cardio-app.coe332.tacc.cloud/jobs/max_affected -X POST -d '{"year":"2014","topic":"Coronary Heart Disease","break_out":"65+"}' -H "Content-Type: application/json"`

- Route: `/jobs/delete`
\t- Purpose: DELETE route deletes all jobs that have been submitted (but are not in progress or completed).
\t- Example:
\t\t- Local laptop: `curl cardio-app.coe332.tacc.cloud/jobs/delete -X DELETE`

- Route: `/jobs/<jobid>`
\t- Purpose: GET route returns the input parameters, job type, and status of the job. jobid is a string (unique identifier for a specific job).
\t- Example:
\t\t- Internet: `cardio-app.coe332.tacc.cloud/jobs/<"specific_job_id">`
\t\t- Local laptop: `curl cardio-app.coe332.tacc.cloud/jobs/<"specific_job_id"> -X GET`

- Route: `/results/<jobid>`
\t- Purpose: GET route returns the results of a specific job. jobid is a string (unique identifier for a specific job).
\t- Example:
\t\t- Internet: `cardio-app.coe332.tacc.cloud/results/<"specific_job_id">`
\t\t- Local laptop: `curl cardio-app.coe332.tacc.cloud/results/<"specific_job_id"> -X GET`
"""
    return route_info


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


@app.route('/jobs/<functName>', methods=['POST'])
def submit_job(functName:str):
    """
    Function is used to submit jobs to the queue.
    Args:
        functName: an input function name argument (that will be called in the worker.py file)
    Returns:
        job_dict: a dictionary of the job information (the input parameters, function name, current status (submitted), etc.)
    """
    logger.info(f"Received POST request for job '{functName}'.")
    worker_functs = ["return_topics","test_work","max_affected", "graph_rf"]
    if not(functName in worker_functs):
         return jsonify({"error": "Invalid function name."}), 400
    should_continue = True
    data = request.get_json()
     
    if functName == "return_topics":
        data = {} # no data needed

    elif functName == "test_work":
        data = {}
    elif functName == "max_affected":

        paras = ["topic", "year","break_out"]
        for elem in paras:
            try:
                x = data[elem]
            except:
                data[elem] = ""
    elif functName == "graph_rf":
        paras = {'breakout', 'risk_factors', 'disease', 'location'}
        keys_set = set(data.keys())
        if keys_set > paras:
            logger.warning("Invalid parameters")
            return jsonify({"Error": f"Invalid parameters for graph_rf in {paras}"})
        # Check if the sorted keys contains at least disease and risk factor
        if ('risk_factors' not in keys_set) and ('disease' not in keys_set):
            logger.warning("Must contain disease and risk_factors")
            return jsonify({"Error": f"Parameters must contain 'disease' and 'risk_factors'"})
        # test if brekaout is a valid breakout
        if 'breakout' in keys_set:
            breakout_list = ["Male","Other", "Female", "75+", "Non-Hispanic Asian", "Non-Hispanic White", "Overall", "Hispanic", "65+", "45-64", "20-24", "Non-Hispanic Black", "35+", "25-44", "18-24"]
            if data['breakout'] not in breakout_list:
                return jsonify({"Error": f"{data['breakout']} not a valid parameter for breakout. Valid parameters include {breakout_list}"})
        if 'location' in keys_set:
            location_param1 = all_categories('locationdesc')
            location_param2 = all_categories('locationabbr')
            if (data['location'] not in location_param1) and (data['location'] not in location_param2):
                return jsonify({"Error": f"{data['location']} not a valid parameter for location. Valid parameters include {location_param1}"})
        # test if rf is a valid rf and if disease is a valid disease
        # rf_list = ["Obesity", "Hypertension", "Physical Inactivity", "Cholesterol Abnormalities", "Smoking", "Diabetes", "Nutrition"]
        rf_list = ["current smoking", "diabetes", "hypertension medication use", "physical inactivity", "consuming fruits and vegetables less than 5 times per day", "high total cholesterol", "cholesterol screening in the past 5 years", "obesity", "hypertension"]
        dis_list = ["stroke", "acute myocardial infarction (heart attack)",  "coronary heart disease", "major cardiovascular disease"]
        for rf in data['risk_factors']:
            if rf.lower() not in rf_list:
                return jsonify({"Error": f"{rf} not a valid parameter for risk factor. Valid parameters include {rf_list}"})
        if data['disease'].lower() not in dis_list:
            return jsonify({"Error": f"{data['disease']} not a valid parameter for location. Valid parameters include {dis_list}"})
    
    # Add job to the queue
    if should_continue:
        job_dict = add_job(functName, data)
        return job_dict


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
    """
    Function checks if result has been posted, this function is the main checker and is used by get_result.
    Args:
        jid (str): the job id
    Returns:
        the result ( a dictionary)
        OR
        error message (dictionary)
    """
    result = res_db.get(jid)
    if result is not None:
        if get_job(jid)['function_name'] == 'graph_rf':
            result = f"Image is available for download with the route /download/{jid}"
            return result
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

@app.route('/data/<category>', methods=['GET'])
def all_categories(category:str):
    '''
    Function returns all the available parameters for a given category
    ArgsL
        category (str): Name of category
    Returns:
        parameters_list (list): List of all available parameters
    '''
    parameters_list = []
    for key in rd.keys():
        data = json.loads(rd.get(key))
        try:
            param = data[category]
        except KeyError:
            return f"Error: {category} is not a valid category. Valid categories include {data.keys()}\n"
        if param not in parameters_list:
            parameters_list.append(param)
    return parameters_list

@app.route('/download/<jobid>', methods=['GET'])
def download(jobid:str):
    path = f'/app/{jobid}.png'
    with open(path, 'wb') as f:
        f.write(res_db.get(jobid))
    return send_file(path, mimetype='image/png', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)










