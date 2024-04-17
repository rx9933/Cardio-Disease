import requests
import time

def test_return_topics() -> None:
    """
    Test the 'return_topics' job submission and result retrieval.

    Returns:
        None

    Args:
        None
    """
    response = requests.post('http://localhost:5000/data')
    response = requests.post('http://localhost:5000/jobs/return_topics', json={})

    assert response.status_code == 200

    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())

    job_id = response.json()["id"]
    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert isinstance(response.json(), list)
    assert isinstance(response.json()[0], str)

def test_max_affected() -> None:
    """
    Test the 'max_affected' job submission and result retrieval.

    Returns:
        None

    Args:
        None
    """
    response = requests.post('http://localhost:5000/jobs/max_affected', json={})

    assert response.status_code == 200

    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())

    response = requests.post('http://localhost:5000/jobs/max_affected', json={"year": "2014", "topic": "Stroke", "break_out": "65+"})
    job_id = response.json()["id"]

    assert response.status_code == 200

    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())

    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert response.json()["year"] == "2014"
    assert response.json()["topic"] == "Stroke"
    assert response.json()["break_out"] == "65+"

def test_test_work() -> None:
    """
    Test the 'test_work' job submission and result retrieval.

    Returns:
        None

    Args:
        None
    """
    response = requests.post('http://localhost:5000/jobs/test_work', json={})

    assert response.status_code == 200

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
