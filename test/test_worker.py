import requests
import time
from worker.py import detrend_data, plot_data, calculate_correlation
from unittest import mock

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

def test_graph_rf():
    response = requests.post('http://localhost:5000/jobs/graph_rf', json={})

    assert response.status_code == 200

    # test when expected result is acheived
    
    # test when there is no data found

def test_select_series():
    # mock rd?

    # test when there is no data to be added in the series

    # test when you get the expected result

def test_detrend_data():
    xy = {0.5: 9.25, 1: 7.6, 1.5: 8.25, 2: 6.5, 2.5: 5.45, 3: 4.5, 3.5: 1.75, 4: 1.8}
    assert isinstance(detrend_data(xy), dict)
    assert detrend_data(xy)[0.5] == pytest.approx(9.25 - (10.657 - 2.231*0.5))
    assert isinstance(detrend_data(xy)[2], float)

def test_correlation():
    response = requests.get(f'http://localhost:5000/jobs/correlation', json={})
    assert = response.status_code == 200
    # test the correlations function

def test_calculate_correlation():
    # abc
    x = [1, 2, 3, 4, 5]
    y = [1, 2, 3, 4, 5]
    x2 = [43, 21, 25, 42, 57, 59]
    y2 = [99, 65, 79, 75, 87, 81]
    assert calculate_correlation(x, y) == pytest.approx(1.0)
    assert calculate_correlation(x2, y2) == pytest.approx(0.5298)

def test_plot_data():
    xy_data = {"linear graph": {1:1, 2:2, 3:3, 4:4, 5:5}, "quadratic": {1:1, 2:4, 3:9, 4:16}}
    plot_data(xy_data, "title", "x_label", "y_label")
    # tests from the internet??
    mock_plt.title.assert_called_once_with("title")
    mock_plt.xlabel.assert_called_once_with("x_label")
    mock_plt.ylabel.assert_called_once_with("y_label")
    assert mock_plt.figure.called

