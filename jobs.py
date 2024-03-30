import json
import uuid
import redis
from hotqueue import HotQueue

_redis_ip='redis-db'
_redis_port='6379'

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
    
def add_job(functName, parameters, status="submitted"):
    # parameters = {} dictionary with required values for calculation
    # functName = string of which function needs to be called in the worker.py file
    """Add a job to the redis queue."""
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, functName, parameters)
    _save_job(jid, job_dict)
    _queue_job(jid)
    return job_dict

def get_job_by_id(jid):
    """Return job dictionary given jid"""
    try:
        return json.loads(jdb.get(jid))
    except:
        return "error"

def update_job_status(jid, status, output={}):
    """Update the status of job with job id `jid` to status `status`."""
    job_dict = get_job_by_id(jid)
    if job_dict:
        job_dict['status'] = status
        job_dict['result'] = output
        _save_job(jid, job_dict)
    else:
        raise Exception()