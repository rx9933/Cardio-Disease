[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#routes)
# Routes
1. Redis Functionality
    * To add data to Redis:
    ```bash
      curl localhost:5000/data -X POST
    ```
    This will return:
    ```bash
      Data posted successfully
    ```
    
    * To retrieve data from Redis:
    ```bash
      curl localhost:5000/data -X GET
    ```
    This should return a long list of dictionaries of cardiovascular data.
    
    * To delete data from Redis:
    ```bash
      curl localhost:5000/data -X DELETE
    ```
    This should return:
    ```bash
      Data deleted successfully
    ```
  
    *Note*: Data on Redis is required for any data analysis; that is how the worker.py gets the data as input. As such, data deletion is not advised to be performed before adding/curling job requests. Doing so will result in empty/uninteresting results as output. 
   
2. Job Functionality
    * To add a job:
    ```bash
      curl localhost:5000/<functionName> -X POST -d '{"parameter key 1": "input data 1", "parameter key 2": "input data 2"}' -H "Content-Type: application/json"
    ```
   "functionName" should be replaced with a specific worker.py function name, based on the functionality desired for the particular job. View below (Job Functions          section) for more details and example jobs. The dictionary containing "parameter key 1" and "parameter key 2" is a dictionary of any size (based on the             required information for the specific worker.py function). The job's details (including a job-specific, unique ID) will be returned as a dictionary after the       job is posted.
   *Note*: ensure that the input dictionary is of strings; both the keys and values must be strings.

   * To remove all jobs that have not begun (leaves only complete or in-progress jobs):
   ```bash
     curl localhost:5000/jobs/delete -X DELETE
   ```
   
    * To list all existing jobs (IDs):
   ```bash
     curl localhost:5000/jobs -X GET
   ```
   Returns a list of all job IDs that have been submitted, are in-progress, or are completed. 
  
    * To return information about a specific job (status):
   ```bash
     curl localhost:5000/jobs/<"specific_job_id"> -X GET
   ```
   "specific_job_id" should be replaced with the desired job ID. View "To add a job" and "To list all existing jobs" for information on retrieving specific job IDs.

   * To return information about a specific job (the output/results):
   ```bash
     curl localhost:5000/results/<"specific_job_id"> -X GET
   ```
   "specific_job_id" should be replaced with the desired job ID. View "To add a job" and "To list all existing jobs" for information on retrieving specific job IDs. 
     *Note*: interesting results will only be output when the job is complete; check for completion status with the previous command. 
   
[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#Job Functions)
# Job Functions
There are currently 3 job functions that can be run. Note that these are in addition to the flask routes detailed in Redis Functionality (1). Each of the commands listed in Job Functionality can be applied to each of the 3 jobs (test_work, return_topics, and max_affected). *Note*: for the example routes shown below, the job id should be replaced with the job id that the user's receive to screen. 
1. test_work: this function is just a work simulation. No real analysis is performed; the worker just sleeps for 20 seconds before returning a random output.
      * To instantiate a job for return_topics:
   ```bash
      curl localhost:5000/test_work -X POST -d '{}' -H "Content-Type: application/json"
   ```
   Note that any input parameters can be input, but they will be ignored since this function does not require any input from users.
   this will return:
   ```bash
      {
     "function_name": "test_work",
     "id": "88e0881c-93c8-49ef-b035-c70b594a6ec3",
     "input_parameters": {},
     "status": "submitted"
   }
   ```
   * To check the status of the job:
   ```bash
      curl localhost:5000/jobs/88e0881c-93c8-49ef-b035-c70b594a6ec3
   ```
      this will return:
   ```bash
   {
     "function_name": "test_work",
     "id": "88e0881c-93c8-49ef-b035-c70b594a6ec3",
     "input_parameters": {},
     "status": "in progress"
   }
   ```
   or the status will be completed/submitted.
   
   * To get the results of the job:
    ```bash
       curl localhost:5000/results/88e0881c-93c8-49ef-b035-c70b594a6ec3
    ```
    this will return:
   ```bash   
        {
     "random output parameter 1": "1st output parameter value"
   }
   ```
   or if the job is not complete:
   ```bash
      Result not found for the specified Job ID. Check completion status of job.
   ```
   
2. return_topics: this function returns the cardiovascular topics that are investigated (Acute Myocardial Infarction, Stroke, etc.).
   * To instantiate a job for return_topics:
   ```bash
      curl localhost:5000/return_topics -X POST -d '{}' -H "Content-Type: application/json"
   ```
   Note that any input parameters can be input, but they will be ignored since this function does not require any input from users.
   this will return:
   ```bash
      {
     "function_name": "return_topics",
     "id": "80df529b-6f2c-4ec8-adf8-2990e85a37af",
     "input_parameters": {},
     "status": "submitted"
   }
   ```
   * To check the status of the job:
   ```bash
      curl localhost:5000/jobs/80df529b-6f2c-4ec8-adf8-2990e85a37af
   ```
      this will return:
   ```bash
      {
        "function_name": "return_topics",
        "id": "80df529b-6f2c-4ec8-adf8-2990e85a37af",
        "input_parameters": {},
        "status": "in progress"
      }
   ```
   or the status will be completed/submitted.
   
   * To get the results of the job:
    ```bash
       curl localhost:5000/results/80df529b-6f2c-4ec8-adf8-2990e85a37af
    ```
    this will return:
   ```bash   
      [
     "Acute Myocardial Infarction (Heart Attack)",
     "Stroke",
     "Coronary Heart Disease",
     "Major Cardiovascular Disease"
   ]
   ```
   or if the job is not complete:
   ```bash
      Result not found for the specified Job ID. Check completion status of job.
   ```
3. max_affected: returns the population with the maximum rates of a particular cardiovascular disease. Based on input parameters, the user can restrict the app to check for a particular cardiovascular disease (i.e., stroke) and/or a particular break out category (either in gender, race, or age) and/or a particular year (i.e. 2013).
   * To instantiate a job for max_affected:
   ```bash
      curl localhost:5000/max_affected -X POST -d '{"year":"2014","topic":"Coronary Heart Disease","break_out":"65+"}' -H "Content-Type: application/json"
   ```
   Note that any input parameters can be used, even with different/wrong keys. If the correct keys are input with inaccurate/nonvalid values (i.e, year = -1990), then no values will be output (the app cannot find values that suite the input parameters). If the wrong keys are input, (i.e., lyear = 2014), then this input parameter will be ignored as well.
   this will return:
   ```bash
      {
     "function_name": "max_affected",
     "id": "dae2b9cf-f04a-4a67-a564-fa3530fc1d89",
     "input_parameters": {
       "break_out": "65+",
       "topic": "Coronary Heart Disease",
       "year": "2014"
     },
     "status": "submitted"
      }
   ```
   * To check the status of the job:
   ```bash
      curl localhost:5000/jobs/dae2b9cf-f04a-4a67-a564-fa3530fc1d89
   ```
      this will return:
   ```bash
         {
     "function_name": "max_affected",
     "id": "dae2b9cf-f04a-4a67-a564-fa3530fc1d89",
     "input_parameters": {
       "break_out": "65+",
       "topic": "Coronary Heart Disease",
       "year": "2014"
     },
     "status": "in progress"
      }
   ```
   or the status might be completed/submitted.
   
   * To get the results of the job:
    ```bash
       curl localhost:5000/results/dae2b9cf-f04a-4a67-a564-fa3530fc1d89
    ```
    this will return:
   ```bash
      {
     "break_out": "65+",
     "break_out_category": "Age",
     "breakoutcategoryid": "BOC03",
     "breakoutid": "AGE06",
     "category": "Cardiovascular Diseases",
     "categoryid": "C1",
     "data_value": "16.8",
     "data_value_alt": "16.8",
     "data_value_type": "Crude",
     "data_value_typeid": "Crude",
     "data_value_unit": "Percent (%)",
     "datasource": "BRFSS",
     "geolocation": {
       "coordinates": [
         -92.44568007099969,
         31.31266064400046
       ],
       "type": "Point"
     },
     "highconfidencelimit": "18.9",
     "indicator": "Prevalence of coronary heart disease among US adults (18+); BRFSS",
     "indicatorid": "BR002",
     "locationabbr": "LA",
     "locationdesc": "Louisiana",
     "locationid": "22",
     "lowconfidencelimit": "14.9",
     "priorityarea1": "None",
     "priorityarea3": "None",
     "row_id": "BRFSS~2014~22~BR002~AGE06~Crude",
     "topic": "Coronary Heart Disease",
     "topicid": "T4",
     "year": "2014"
   }
   ```
   or, if job status is "in progress" or "submitted":
   ```bash
      Result not found for the specified Job ID. Check completion status of job.
   ```
   

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#Unit Testing)
# Unit Testing
1. Follow "To Build Image", then, in the same directory as the homework08 repository, run the following command:
```bash
pytest
```
Note: a different terminal (as long as it has Docker installed and has been navigated to the homework08 directory) can run the <pytest> command, as long as the docker image has been correctly pulled and is running (view "To Build Image").

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#Debugging)
## Launching Containers
* If the following error appears:
 ```bash
   curl: (7) Failed to connect to localhost port 5000 after 0 ms: Connection refused
 ```
 the docker containers where not properly launched. Repeat "To Build Image" and try route again.

 * If the following error appears when applying pytest:
   ```bash
      ====================================== short test summary info ======================================
   FAILED test_api.py::test_all_jobs - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie...
   FAILED test_api.py::test_submit_job - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie...
   FAILED test_api.py::test_invalid_function_name - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie...
   FAILED test_api.py::test_get_job - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie...
   FAILED test_api.py::test_get_result_by_id - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie...
   FAILED test_api.py::test_add_and_delete_job - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie...
   FAILED test_api.py::test_post_data - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie...
   FAILED test_api.py::test_get_data - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie...
   FAILED test_api.py::test_delete_data - requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=5000): Max retrie..
   ```
   the docker containers where not properly launched. Repeat "To Build Image" and try route again.
   
## Understanding Results
* If max_affected or return_topics returns empty lists/dictionaries as output, then you probably have not posted the data to redis. Make sure to post the data to redis (do not delete it) and then try the job again.
* If the job is not completed, and you try to get the results with "curl localhost:5000/results/<"specific_job_id"> -X GET", then, the following result will be output:
```bash
Result not found for the specified Job ID. Check completion status of job.
```
Try to check the status of the job with "curl localhost:5000/jobs/<"specific_job_id"> -X GET" and make sure the status is "complete" before trying to check the results. 
* 

