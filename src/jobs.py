import logging
import json
import uuid
import redis
import os
from hotqueue import HotQueue
#from worker import res_db

_redis_ip = os.environ.get('REDIS_IP','environment not found')
_redis_port = '6379'

rd = redis.Redis(host=_redis_ip, port=6379, db=0)
q = HotQueue("queue", host=_redis_ip, port=6379, db=1)
jdb = redis.Redis(host=_redis_ip, port=6379, db=2)



# Read the log level from the environment variable
log_level = os.environ.get('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)


def _generate_jid():
    """
    Function gnerate a pseudo-random identifier for a job.
    Args:
        None
    Returns:
        str: an ID string
    """
    return str(uuid.uuid4())

def _instantiate_job(jid:str,status:str, functName:str, parameters:dict):
    """
    Function creates the job object description as a python dictionary. Requires the job id,
    status, start and end parameters.
    Args:
        jid: job id, a string
        status: completion status (whether the job is queue, in progress, or completed)
        functName: the worker function that will be required (the type of analysis that is desired).
        parameters: the input parameters required for the work
    Returns:
        a dictionary of the input argumets.
    """
    return {'id': jid,
            'status':status,
            'function_name': functName,
            'input_parameters': parameters,
            }

def _save_job(jid:str, job_dict:dict):
    """
    Function save a job object in the jobs database.
    Args:
        jid: specific job id
        job_dict: a dictionary of the status, functName, parameters, and jid
    Return:
        None
    """
    # Convert dict_keys to list
    job_dict = dict(job_dict)
    jdb.set(jid, json.dumps(job_dict))


def _queue_job(jid:str):
    """
    Function adds a job to the jobs queue.
    Args:
        jid: job id
    Return:
         None
    """
    q.put(jid)
    return

def delete_jobs():
    """
    Function deletes the jobs that are in the queue; leaves the jobs that are completed or in progress.
    Args:
        None
    Return:
        None
    """
    q.clear()
#    jdb.flushdb() # add this to remove all jobs (even finished ones)
    keys = jdb.keys()  # Get all keys (job IDs) from the job database
    for key in keys:
        job_dict = json.loads(jdb.get(key))
        logging.warning(f"{job_dict}")
        if job_dict['status'] == 'submitted':
            jdb.delete(key)  # Delete the job from the database
    return

def update_job_status(jid:str, status:str, output={}):
    """
    Function updates the status of job with job id `jid` to status `status`.
    Args:
        jid: job id
        status: completion status, a string of complete, in progress, or submitted.
        output: the analysis output, optional input argument; default is an empty dictionary, could be list
    Returns:
        job_dict: a dictionary of the status, output, and other information about the job.
        OR: if users input an incorrect functName:
        an error dictiionary: returns a dictionary of describing the error (incorrect function call in worker.py)
    """
    job_dict = get_job_by_id(jid)
    if job_dict:
        new_job_dict = job_dict.copy()  # Create a copy of the job dictionary
        new_job_dict['status'] = status
        _save_job(jid, new_job_dict)  # Save the updated job dictionary
        return new_job_dict
    else:
        logger.error("Job with ID %s not found when updating status", jid)
        return {"error": "incorrect function call"}


def add_job(functName:str,parameters:dict, status="submitted"):
    """
    Function adds job to queue. Or, if incorrect input function (worker.py function) returns an error.
    Args:
        functName: a string of the function that is should be used in worker.py
        parameters: input parameters required for analysis
    Returns:
        job_dict: a dictionary of all the job's associated information (before analysis)
        OR:
        job_dict: the original job's dictionary with an error message due to incorrect function call.
       """
    # parameters = {} dictionary with required values for calculation
    # functName = string of which function needs to be called in the worker.py file
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, functName, parameters)

    worker_functs = ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'cardio_data', 'do_work', 'return_topics', 'test_work','max_affected', 'graph_rf', 'correlation']
    if functName not in worker_functs:
         logger.warning("Incorrect function call for job with ID %s", jid)
         update_job_status(jid, "error", output={"incorrect function call": "job not submitted"})
 #       return job_dict
         job_dict['error'] = "incorrect function call"
         return job_dict
    _save_job(jid, job_dict)
    _queue_job(jid)
    return job_dict

def get_job_by_id(jid:str):
    """
    Function return job dictionary (with status and, possibly, an output) given jid.
    Args:
        jid: job id of job in queue.
    Returns:
        a dictionary of the job information (with the status, output, function name, input parameters, etc.)
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
    job_dict = jdb.get(jid)
    if job_dict is not None:
        return json.loads(job_dict)
    else:
        logger.warning("Job with ID %s not found", jid)
        return {"error":"job not found"}  # Return an empty dictionary if job not found


def get_all_job_ids():
    """
    Function returns a list of all existing job IDs.
    Args:
        None
    Returns:
        a list of job id strings.
    """
    keys = jdb.keys()  # Get all keys from the job database
    return [key.decode('utf-8') for key in keys]  # Convert keys to strings and return as a list













