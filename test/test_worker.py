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



    # Test when no data is found satisfying the specified inputs
    para = {"topic": "Nonexistent Disease", "year": "2020", "break_out": ""}
    assert max_affected(para) == "No data of this type can be found to analyze.\n"


    # Test when data is found satisfying the specified inputs
    para = {"topic": "Coronary Heart Disease", "year": "2014", "break_out": "65+"}
    expected_result = {
        "topic": "Coronary Heart Disease",
        "year": "2014",
        "break_out": "65+",
        "data_value": "22.3"
    }
    assert max_affected(para) == expected_result


    # Test when data is found satisfying the specified inputs but missing "data_value" key
    para = {"topic": "Coronary Heart Disease", "year": "2015", "break_out": ""}
    assert max_affected(para) == "No data of this type can be found to analyze.\n"


    # Test when data is found satisfying the specified inputs but with invalid "data_value" (not a float)
    para = {"topic": "Coronary Heart Disease", "year": "2016", "break_out": "18-24"}
    assert max_affected(para) == "No data of this type can be found to analyze.\n"


    # Test when input parameters are invalid (e.g., missing "topic" key)
    para = {"year": "2017", "break_out": "25-34"}
    assert max_affected(para) == "No data of this type can be found to analyze.\n"


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
