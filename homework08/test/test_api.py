import pytest
from flask import jsonify
import requests
#from src.api import validate_year
from homework08.src.api import validate_year
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
    


