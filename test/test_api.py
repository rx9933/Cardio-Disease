from flask import jsonify
import requests
import logging
import os
import time

# Read the log level from the environment variable
log_level = os.environ.get('LOG_LEVEL', 'INFO')

# Configure logging
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

def test_help() -> None:
    """
    Tests the / route for the help method.
    
    Returns:
        None
    
    Args:
        None
    """
    response = requests.get("http://localhost:5000/")
    assert response.status_code == 200
        
def test_all_jobs() -> None:
    """
    Test the /jobs route for GET method.

    Returns:
        None

    Args:
        None
    """
    response = requests.get("http://localhost:5000/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_submit_job() -> None:
    """
    Test the /<functName> route for POST method.

    Returns:
        None

    Args:
        None
    """
    response = requests.post('http://localhost:5000/jobs/max_affected', json={"year": "2000"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "id" in response.json()
    assert "status" in response.json()
    assert "function_name" in response.json()
    assert "input_parameters" in response.json()

def test_invalid_function_name() -> None:
    """
    Test submitting a job with an invalid function name.

    Returns:
        None

    Args:
        None
    """
    response = requests.post('http://localhost:5000/jobs/invalid_function_name')
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid function name."}

def test_get_job() -> None:
    """
    Test getting job status/job dict.

    Returns:
        None

    Args:
        None
    """
    response = requests.post('http://localhost:5000/jobs/return_topics', json={"start": "1999", "end": "2000"})
    keys = [ "function_name", "id", "input_parameters", "status"]
    assert set(keys) == set(list(response.json().keys()))
    response = requests.post('http://localhost:5000/jobs/max_affected', json={})
    keys = [ "function_name", "id", "input_parameters", "status"]
    assert set(keys) == set(list(response.json().keys()))

def test_get_result_by_id() -> None:
    """
    Test getting result by job ID.

    Returns:
        None

    Args:
        None
    """
    # Submit a job to get a valid job ID
    response = requests.post('http://localhost:5000/data')
    assert response.status_code == 200
    assert response.text == "Data posted successfully\n"

    response = requests.post('http://localhost:5000/jobs/return_topics', json={"start": "1999", "end": "2000"})
    job_id = response.json()["id"]

    # Wait for the job to complete (assuming the job status changes to 'completed' when it's done)
    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break

    # Retrieve the result using the valid job ID
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    logging.error(f"{response.json()}")
    logging.error(f"{response.json()[0]}")
    assert isinstance(response.json()[0],str)

    # Assuming there is no job with ID '456' in the system
    response = requests.get('http://localhost:5000/results/456')
    assert response.text == "Result not found for the specified Job ID. Check completion status of job. \n"

def test_add_and_delete_job() -> None:
    """
    Test adding and deleting jobs.

    Returns:
        None

    Args:
        None
    """
    # Add a job
    add_response = requests.post('http://localhost:5000/jobs/test_work',json={})
    assert add_response.status_code == 200

    add_response = requests.post('http://localhost:5000/jobs/test_work',json={})
    assert add_response.status_code == 200

    job_id = add_response.json()["id"]
    logging.error(f"{requests.get(f'http://localhost:5000/jobs/{job_id}').json()}")


    # Delete all jobs
    delete_response = requests.delete('http://localhost:5000/jobs/delete')
    assert delete_response.status_code == 200
    assert delete_response.text == "all jobs have been deleted off of worker queue. \n"

    # Check if the job is still in the queue
    job_id = add_response.json()['id']
    job_status_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
    assert job_status_response.status_code == 200
    assert job_status_response.json() == {"error": "job not found"}

    # add a correlation job
    url = 'http://localhost:5000/jobs/correlation'
    data = {
        'breakout': 'Overall',
        'risk_factors': ['Obesity', 'Physical Inactivity', 'consuming fruits and vegetables less than 5 times per day'],
        'disease': 'Coronary Heart Disease',
        'location': 'Texas'
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=data, headers=headers)
    assert add_response.status_code == 200
    

def test_post_data() -> None:
    """
    Test posting data.

    Returns:
        None

    Args:
        None
    """
    response = requests.post('http://localhost:5000/data')
    assert response.status_code == 200
    assert response.text == "Data posted successfully\n"

def test_get_data() -> None:
    """
    Test getting data.

    Returns:
        None

    Args:
        None
    """
    response = requests.get('http://localhost:5000/data')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_all_categories() -> None:
    """
    Tests all_categories function in api.py.

    Returns:
       None

    Args:
       None
    """
    response = requests.get('http://localhost:5000/data/break_out')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    expected_values = [
    "Male", "75+", "35+", "Non-Hispanic Asian", "Non-Hispanic Black", "Overall",
    "Hispanic", "Female", "45-64", "Non-Hispanic White", "65+", "Other", "18-24",
    "25-44", "20-24"
    ]

    # Convert both the expected and actual JSON arrays to sets
    expected_set = set(expected_values)
    actual_set = set(response.json())

    # Check if the sets are equal
    assert expected_set == actual_set

    response = requests.get('http://localhost:5000/data/year')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_download_job() -> None:
    """
    Tests download job function in api.py.

    Returns:
       None

    Args:
       None
    """
    url = 'http://localhost:5000/jobs/graph_rf'
    data = {'disease': 'stroke', 'risk_factors': ['current smoking'], 'location': 'Texas','breakout_params': '65+'}
    
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=data, headers=headers)
    assert response.status_code == 200

    job_id = response.json()["id"]
    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert response.status_code == 200

    url = 'http://localhost:5000/jobs/correlation'
    data = {
        'breakout': 'Overall',
        'risk_factors': ['Obesity', 'Physical Inactivity', 'consuming fruits and vegetables less than 5 times per day'],
        'disease': 'Coronary Heart Disease',
        'location': 'Texas'
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=data, headers=headers)
    job_id = response.json()["id"]
    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert response.status_code == 200

    
def test_delete_data() -> None:
    """
    Test deleting data.

    Returns:
        None

    Args:
        None
    """
    response = requests.delete('http://localhost:5000/data')
    assert response.status_code == 200
    assert response.text == "Data deleted successfully\n"
