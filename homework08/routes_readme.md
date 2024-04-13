[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#routes)

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

There are currently 4 job functions that can be run. Note that these are in addition to the flask routes detailed in Redis Functionality (1). Each of the commands listed in Job Functionality can be applied to each of the 4 jobs (test_work, max_affected, return_year_data, and return_topics). 


[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#Unit Testing)
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
* If max_affected, return_year_data, or return_topics returns empty lists/dictionaries as output, then you probably have not posted the data to redis. Make sure to post the data to redis (do not delete it) and then try the job again.
* If the job is not completed, and you try to get the results with "curl localhost:5000/results/<"specific_job_id"> -X GET", then, the following result will be output:
```bash
Result not found for the specified Job ID. Check completion status of job.
```
Try to check the status of the job with "curl localhost:5000/jobs/<"specific_job_id"> -X GET" and make sure the status is "complete" before trying to check the results. 
* 

