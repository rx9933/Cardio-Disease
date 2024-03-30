import time
import json  # Add this import

from jobs import get_job_by_id, update_job_status, q, rd

def return_data(jid, job_outdict):
    rd.set(jid, json.dumps(job_outdict))  # Corrected to use rd instead of jdb
    return

@q.worker
def do_work(jobid):
    update_job_status(jobid, 'in progress')
    time.sleep(10)  # Simulating some work
    output = {"random output parameter 1": "1st output parameter value"}  # Corrected output format
    status = "complete"
    update_job_status(jobid, status, output)

if __name__ == '__main__':
    do_work()
