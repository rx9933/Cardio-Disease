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
    """
    Test the /jobs/<jobid> route for GET method.
    """
    # Assuming jobid exists in the database

    response = requests.post('http://localhost:5000/return_year_data', json={"start": "1999", "end": \
"2012"})
    jobid = response.json()["id"]
    response = requests.get(f"http://localhost:5000/results/{jobid}")
    assert response.status_code == 200
    logging.error( requests.get(f"http://localhost:5000/jobs/{jobid}"))
    while isinstance(requests.get(f"http://localhost:5000/jobs/{jobid}"),str):# == "Result not found for the specified Job ID. Check completion status of job. \n":
        time.sleep(.01)
        pass
    logging.warning(f"{response}") 
    assert isinstance(requests.get(f"http://localhost:5000/jobs/{jobid}").json(), dict)


    datapost = requests.post("http://localhost:5000/data")

    assert datapost.content == b'Data posted successfully\n'



    response = requests.post('http://localhost:5000/return_year_data', json={"start": "1999", "end": \
\
"2012"})
    jobid = response.json()["id"]
    response = requests.get(f"http://localhost:5000/results/{jobid}")
    assert response.status_code == 200


    ###################################


    assert response.text == "Result not found for the specified Job ID. Check completion status of jo\
b. \n"

    assert isinstance(response.json(), dict)

    assert "id" in response.json()
    assert "status" in response.json()
    assert "output" in response.json()
    assert "function_name" in response.json()
    assert "input_parameters" in response.json()

    # Assuming jobid does not exist in the database
    invalid_jobid = "invalid_jobid"
    response = requests.get(f"http://localhost:5000/results/{invalid_jobid}")
    assert response.status_code == 200
    assert response.text == "Result not found for the specified Job ID. Check completion status of job. \n"


