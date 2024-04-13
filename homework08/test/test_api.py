import pytest
from flask import jsonify
import requests
#from src.api import validate_year
#from homework08.src.api import validate_year
import logging
import os
import time
# Read the log level from the environment variable
log_level = os.environ.get('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

def test_all_jobs():
    """
    Test the /jobs route for GET method.
    """
    response = requests.get("http://localhost:5000/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
"""
def test_validate_year():
    data = {"a":1,"b":2}
    assert(validate_year(data) == False)
    data = {"start":1,"end":2}
    assert(validate_year(data) == True)
    data = {"a":1,"end":2}
    assert(validate_year(data) == False)
    
"""    
def test_submit_job():
    """
    Test the /<functName> route for POST method.
    """
    response = requests.post('http://localhost:5000/return_year_data', json={"start": "1999", "end": "2000"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "id" in response.json()
    assert "status" in response.json()
    assert "function_name" in response.json()
    assert "input_parameters" in response.json()
        
def test_invalid_function_name():
    """
    Test submitting a job with an invalid function name.
    """
    response = requests.post('http://localhost:5000/invalid_function_name')
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid function name."}

def test_get_job(): # just job status/job dict
    response = requests.post('http://localhost:5000/return_year_data', json={"start": "1999", "end": "2000"})
    keys = [ "function_name", "id", "input_parameters", "status"]
    assert set(keys) == set(list(response.json().keys()))
    response = requests.post('http://localhost:5000/max_affected', json={})
    keys = [ "function_name", "id", "input_parameters", "status"]
    assert set(keys) == set(list(response.json().keys()))


def test_get_result_by_id():
    # Submit a job to get a valid job ID
    response = requests.post('http://localhost:5000/return_year_data', json={"start": "1999", "end": "2000"})
    job_id = response.json()["id"]

    # Wait for the job to complete (assuming the job status changes to 'completed' when it's done)
    while True:
        logging.error(f"{requests.get(f'http://localhost:5000/jobs').json()}")
        logging.error(f"{requests.get(f'http://localhost:5000/jobs/{job_id}').json()}")
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break

    # Retrieve the result using the valid job ID
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    # Assuming there is no job with ID '456' in the system
    response = requests.get('http://localhost:5000/results/456')
#    assert response.status_code == 200
    assert response.text == "Result not found for the specified Job ID. Check completion status of job. \n"



def test_add_and_delete_job():
    # Add a job
    add_response = requests.post('http://localhost:5000/test_work',json={})
    assert add_response.status_code == 200
    
    add_response = requests.post('http://localhost:5000/test_work',json={})
    assert add_response.status_code == 200

    job_id = add_response.json()["id"]
#    logging.error(f"{requests.get(f'http://localhost:5000/jobs').json()}")
    logging.error(f"{requests.get(f'http://localhost:5000/jobs/{job_id}').json()}")
    # Delete all jobs
    curr = requests.get(f"http://localhost:5000/jobs/{job_id}").json()["status"]
    assert not(curr == "completed") and not(curr=="in progress")
    delete_response = requests.delete('http://localhost:5000/jobs/delete')
    assert delete_response.status_code == 200
    assert delete_response.text == "all jobs have been deleted off of worker queue. \n"

    # Check if the job is still in the queue
    job_id = add_response.json()['id']
    job_status_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
    assert job_status_response.status_code == 200
    assert job_status_response.json() == {"error": "job not found"}
    
def test_post_data():
    # Send a POST request to add data
    response = requests.post('http://localhost:5000/data')
    assert response.status_code == 200
    assert response.text == "Data posted successfully\n"

def test_get_data():
    # Send a GET request to retrieve all data
    response = requests.get('http://localhost:5000/data')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_data():
    # Send a DELETE request to delete all data
    response = requests.delete('http://localhost:5000/data')
    assert response.status_code == 200
    assert response.text == "Data deleted successfully\n"

if __name__ == '__main__':
    test_post_data()
    test_get_data()
    test_delete_data()
