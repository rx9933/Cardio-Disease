import requests
import time

def test_return_topics():
    # Send a GET request to submit the job
    response = requests.post('http://localhost:5000/data')
    response = requests.post('http://localhost:5000/return_topics',json ={})

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response contains the expected keys
    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())
    job_id = response.json()["id"]
    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}')    
    assert isinstance(response.json(),list)
    assert isinstance(response.json()[0], str)
    
def test_max_affected():

    # Send a GET request to submit the job
    response = requests.post('http://localhost:5000/max_affected', json = {})

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response contains the expected keys
    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())

    # Send a POST request to submit the job
    response = requests.post('http://localhost:5000/max_affected', json = {"year":"2014", "topic":"Stroke", "break_out":"65+"})
    job_id = response.json()["id"]
    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response contains the expected keys
    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())

    # Wait for the job to complete (assuming the job status changes to 'completed' when it's done)
    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert response.json()["year"] == "2014"
    assert response.json()["topic"] == "Stroke"
    assert response.json()["break_out"] == "65+"

def test_test_work():
    # Send a GET request to submit the job
    response = requests.post('http://localhost:5000/test_work', json ={})

    # Check if the response status code is 200
    assert response.status_code == 200

    # Check if the response contains the expected keys
    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())

    job_id = response.json()["id"]
    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert response.json()["random output parameter 1"] == "1st output parameter value"
    
if __name__ == '__main__':
    test_return_topics()
    test_max_affected()
    test_test_work()
