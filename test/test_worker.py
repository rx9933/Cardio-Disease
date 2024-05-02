import requests
import time
from unittest import mock
from worker import return_topics, max_affected, graph_rf, select_series, plot_data, calculate_correlation, detrend_data
from textwrap import wrap

def test_return_topics() -> None:
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

def test_graph_rf():
    response = requests.post('http://localhost:5000/jobs/graph_rf', json={})

    assert response.status_code == 200

    response = requests.post('http://localhost:5000/jobs/graph_rf', json={"disease":"Stroke", "breakout":"65+", "risk_factors":["Smoking", "Physical Inactivity"], "location":"Texas"})

    assert response.status_code == 200
    assert response.json() == {
  "Error": "Smoking not a valid parameter for risk factor. Valid parameters include ['current smoking', 'diabetes', 'hypertension medication use', 'physical inactivity', 'consuming fruits and vegetables less than 5 times per day', 'high total cholesterol', 'cholesterol screening in the past 5 years', 'obesity', 'hypertension']"
}

    response = requests.post('http://localhost:5000/jobs/graph_rf', json={"disease":"Stroke", "detrend": "True", "breakout":"65+", "risk_factors":["current smoking", "physical inactivity"], "location":"Texas"})
    
    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())

    job_id = response.json()["id"]

    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}').json()
    assert response == f"Image is available for download with the route /download/{job_id}"

def test_select_series():
    out = select_series("Colorado", "65+", "Stroke")
    assert isinstance(out, dict)
    assert out == {'2013': '5.9', '2014': '5.5', '2015': '7', '2019': '5', '2016': '6.2', '2011': '5.7', '2017': '5.6', '2012': '5.9'}

    out = select_series("Colorado", "65+", "rand")
    assert isinstance(out, dict)
    assert out == {}

def test_detrend_data():
    xy = {0.5: 9.25, 1: 7.6, 1.5: 8.25, 2: 6.5, 2.5: 5.45, 3: 4.5, 3.5: 1.75, 4: 1.8}
    assert isinstance(detrend_data(xy), dict)
    assert abs(detrend_data(xy)[0.5] - (9.25 - (10.657 - 2.231*0.5))) <= .1
    assert isinstance(detrend_data(xy)[2], float)

def test_calculate_correlation():
    x = [1, 2, 3, 4, 5]
    y = [1, 2, 3, 4, 5]
    x2 = [43, 21, 25, 42, 57, 59]
    y2 = [99, 65, 79, 75, 87, 81]
    assert calculate_correlation(x, y) == 1.0
    assert abs(calculate_correlation(x2, y2) - 0.5298) <=.1

def test_graph_correlation():
    response = requests.post('http://localhost:5000/jobs/graph_correlation', json={})

    assert response.status_code == 200

    response = requests.post('http://localhost:5000/jobs/graph_correlation', json={"disease":"Stroke", "breakout":"65+", "risk_factors":["Smoking", "Physical Inactivity"], "location":"Texas"})

    assert response.status_code == 200
    assert response.json() == {"Error": "Smoking not a valid parameter for risk factor. Valid parameters include ['current smoking', 'diabetes', 'hypertension medication use', 'physical inactivity', 'consuming fruits and vegetables less than 5 times per day', 'high total cholesterol', 'cholesterol screening in the past 5 years', 'obesity', 'hypertension']"}

    response = requests.post('http://localhost:5000/jobs/graph_correlation', json={"disease":"Stroke", "breakout":"65+", "risk_factors":["current smoking", "physical inactivity"], "location":"Texas"})
    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())
    job_id = response.json()["id"]

    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}').json()
    assert response == f"Image is available for download with the route /download/{job_id}"

def test_correlation():
    response = requests.post('http://localhost:5000/jobs/correlation', json={})

    assert response.status_code == 200

    response = requests.post('http://localhost:5000/jobs/correlation', json={"disease":"Stroke", "breakout":"65+", "risk_factors":["Smoking", "Physical Inactivity"], "location":"Texas"})

    assert response.status_code == 200
    assert response.json() == {"Error": "Smoking not a valid parameter for risk factor. Valid parameters include ['current smoking', 'diabetes', 'hypertension medication use', 'physical inactivity', 'consuming fruits and vegetables less than 5 times per day', 'high total cholesterol', 'cholesterol screening in the past 5 years', 'obesity', 'hypertension']"}

    response = requests.post('http://localhost:5000/jobs/correlation', json={"disease":"Stroke", "breakout":"65+", "risk_factors":["current smoking", "physical inactivity"], "location":"Texas"})

    keys = ['function_name', 'id', 'input_parameters', 'status']
    assert set(keys) == set(response.json().keys())

    job_id = response.json()["id"]

    while True:
        time.sleep(1)
        job_response = requests.get(f'http://localhost:5000/jobs/{job_id}')
        if job_response.json()["status"] == "complete":
            break
    response = requests.get(f'http://localhost:5000/results/{job_id}').json()
    assert response == {"Correlation coefficient between current smoking and stroke": 0.24755237551034065, "Correlation coefficient between physical inactivity and stroke": 0.7364858201822571}
