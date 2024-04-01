<h1 align="center">Cardiovascular Disease</h1>
<p align="center">
  <b>A containerized Flask-Redis-Kubernetes application that analyzes behavioral risk factors on cardiovascular disease. Final Project for COE332 (Software Engineering and Design).</b></br>
  <sub><sub>
</p>

<br />

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#implementation)
#  Implementation

## To Build Image
1. Clone this repository:
```bash
git@github.com:rx9933/COE-332-Homework.git
```
2. Navigate to this directory (homework07). 
3. To run program:
```bash
docker-compose up -d
```
Leave program running while proceeding with Making Requests to Container. Only use "To stop program" when done interacting with app.

4. To stop program:
```bash
docker-compose down
```

## To Make Requests to Running Container
Note: Proceed only if "To Build Image" is complete and the app is running (step 3). 
The following are various curl commands/routes that can be utilized: 

1. To add a job:
```bash
curl localhost:5000/jobs/<"abc"> -X POST -d '{"parameter key 1": input data 1, "parameter key 2": input data 2}' -H "Content-Type: application/json"
```
"abc" should be replaced with a specific worker.py function name, based on the functionality desired of the particular job. View below (worker.py functions) for more details. 
The dictionary containing "parameter key 1" and "parameter key 2" is a dictionary of any size (based on the required information for the specific worker.py function). 
The job's details (including a job-specific, unique ID) will be returned as a dictionary after the job is posted. 

2. To return information about a specific job:
```bash
curl localhost:5000/jobs/<"specific_job_id"> -X GET
```
"specific_job_id" should be replaced with the desired job ID. View "To add a job" and "To list all existing jobs" for information on retreiving specific job IDs. 

3. To list all existing jobs (IDs):
```bash
curl localhost:5000/jobs -X GET
```
Returns a list of all job IDs that have been submitted, are in-progress, or are completed. 

4. To remove all jobs that have not begun (leaves only complete or in-progress jobs):
```bash
curl localhost:5000/jobs/delete -X DELETE
```
5. To return all the topics of the cardiovascular diseasese:
```bash
curl localhost:5000/jobs/"return_topics" -X POST -d '{}'-H "Content-Type: application/json"
```
Note: no input parameters are required for this command (as represented by the empty input dictionary "{}").
return_topics is the function name in the worker.py file. 

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#debugging)
#  Debugging
1. For incorrect commands (function calls):
   After curling an incorrect route (function 1. of Implementation), use function 2. of Implementation to return information about the specific job.
   The following output will be shown:
   ```bash
    {
    "error": "job not found",
    "result": {
      "incorrect function call": "job not submitted"
    },
    "status": "error"
    }
  ```
