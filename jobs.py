import json
import uuid
import redis
import os
from hotqueue import HotQueue

_redis_ip = os.environ.get('REDIS_IP', 'Environment variable does not exist')
_redis_port = '6379'

rd = redis.Redis(host=_redis_ip, port=6379, db=0)
q = HotQueue("queue", host=_redis_ip, port=6379, db=1)
jdb = redis.Redis(host=_redis_ip, port=6379, db=2)

def _generate_jid():
    """
    Generate a pseudo-random identifier for a job.
    """
    return str(uuid.uuid4())

def _instantiate_job(jid, status, functName, parameters):
    """
    Create the job object description as a python dictionary. Requires the job id,
    status, start and end parameters.
    """
    return {'id': jid,
            'status':status,
            'function_name': functName,
            'input_parameters': parameters,
            }

def _save_job(jid, job_dict):
    """Save a job object in the Redis database."""
    jdb.set(jid, json.dumps(job_dict))
    return 

def _queue_job(jid):
    """Add a job to the redis queue."""
    q.put(jid)
    return

def delete_jobs():
    q.clear()
#    jdb.flushdb() # add this to remove all jobs (even finished ones)
    keys = jdb.keys()  # Get all keys (job IDs) from the job database
    for key in keys:
        job_dict = json.loads(jdb.get(key))
        if job_dict['status'] == 'submitted':
            jdb.delete(key)  # Delete the job from the database


'''
def update_job_status(jid, status, output={}):
    """Update the status of job with job id `jid` to status `status`."""
    job_dict = get_job_by_id(jid)
    if job_dict:
        job_dict['status'] = status
        job_dict['result'] = output
        _save_job(jid, job_dict)
    else:
        raise Exception()
'''
def update_job_status(jid, status, output={}):
    """Update the status of job with job id `jid` to status `status`."""
    job_dict = get_job_by_id(jid)
    if job_dict:
        new_job_dict = job_dict.copy()  # Create a copy of the job dictionary
        new_job_dict['status'] = status
        new_job_dict['result'] = output
        _save_job(jid, new_job_dict)  # Save the updated job dictionary
        return job_dict
    else:
#        raise Exception()
        return {"error": "incorrect function call"}



def add_job(functName, parameters, status="submitted"):
    # parameters = {} dictionary with required values for calculation
    # functName = string of which function needs to be called in the worker.py file
    """Add a job to the redis queue."""
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, functName, parameters)

    worker_functs = ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'cardio_data', 'do_work', 'return_topics', 'test_work']
    if functName not in worker_functs:
         update_job_status(jid, "error", output={"incorrect function call": "job not submitted"})
 #       return job_dict
         job_dict['error'] = "incorrect function call"
         return job_dict
    _save_job(jid, job_dict)
    _queue_job(jid)
    return job_dict

'''
def add_job(functName, parameters, status="submitted"):
    # parameters = {} dictionary with required values for calculation
    # functName = string of which function needs to be called in the worker.py file
    """Add a job to the redis queue."""
    worker_functs = ['__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'cardio_data', 'do_work', 'return_topics', 'test_work']
    if functName not in worker_functs:
        error_output = {"error": "incorrect function call"}
        job_dict = {
            'status': 'error',
            'function_name': functName,
            'input_parameters': parameters,
            'result': error_output
        }
        _save_job('error-' + _generate_jid(), job_dict)
        return job_dict

    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, functName, parameters)
    _save_job(jid, job_dict)
    _queue_job(jid)
    return job_dict
'''
'''
def get_job_by_id(jid):
    """Return job dictionary given jid"""
    try:
        return json.loads(jdb.get(jid))
    except:
        return "error"
'''
def get_job_by_id(jid):
    """Return job dictionary given jid"""
    job_dict = jdb.get(jid)
    if job_dict is not None:
        return json.loads(job_dict)
    else:
        return {"error":"job not found"}  # Return an empty dictionary if job not found

def get_all_job_ids():
    """Return a list of all existing job IDs."""
    keys = jdb.keys()  # Get all keys from the job database
    return [key.decode('utf-8') for key in keys]  # Convert keys to strings and return as a list

'''    
def update_job_status(jid, status, output={}):
    """Update the status of job with job id `jid` to status `status`."""
    job_dict = get_job_by_id(jid)
    if job_dict:
        job_dict['status'] = status
        job_dict['result'] = output
        _save_job(jid, job_dict)
    else:
        raise Exception()
'''
