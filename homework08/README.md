<h1 align="center">Cardiovascular Disease</h1>
<p align="center">
  <b>A containerized Flask-Redis application that analyzes behavioral risk factors on cardiovascular disease. Start of Final Project for COE332 (Software Engineering and Design).</b></br>
  <sub><sub>
</p>

<br />

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#purpose)
#  Purpose
The project aims to illuminate various correlations between behavioral patterns and cardiovascular diseases. The app will include:
1. several endpoints for retrieving specific data subsets, such as by class (cardiovascular rates or risk factors), topic (specific cardiovascular diseases or risk factors), location (states), and breakout category (gender, age, or race)
2. functionality to post, delete, and retrieve data from a Redis database
3. visualizations in graphs.
The app's easy functionality for data visualization will allow for widespread access to data patterns and future insights into how lifestyle choices and demographic factors can contribute to cardiovascular health.
Ultimately, the app can help inform public health strategies and interventions.

Currently, step 2 (redis database functionality) is supported along with two other functions: one to simulate work/analysis being done and one to return the major cardiovascular diseases that are measured/parameters in the data file. 

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#data)
#  Data
Data about various behavioral risk factors (leading to cardiovascular disease) is sourced from the CDC: [National Cardiovascular Disease Surveillance Data)](https://data.cdc.gov/Heart-Disease-Stroke-Prevention/Behavioral-Risk-Factor-Surveillance-System-BRFSS-N/ikwk-8git/about_data). The risk surveillance system is provided by the National Cardiovascular Disease Surveillance System, which integrated multiple indicators from different data sources to create a comprehensive list of Cardiovascular Diseases (CVD) and associated risk factors across the United States (with around 10 years worth of tracking). Data parameters include year (2011 to 2022), location (national, regional, state, selected sites), indicators (obesity, smoking, etc.), type of CVD (i.e. stroke or heart failure), age group, sex, and race. There are approximately 160,160 data points. Data was last updated August 25th, 2023. Data can be accessed in either a csv or json format; for this project, the app uses the csv data format.

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#foldercontents)
#  Folder Contents/Program Structure:
The following files are included for correct deployment of this app:
1. "api.py": code that includes flask routes that users can curl/access.
2. "jobs.py": initializes jobs based on user inputs and adds jobs (along with the necessary parameters) to a job queue.
3. "worker.py": takes jobs off of the job queue, computes the value, and returns the value.
4. "requirements.txt": the required versions of python libraries (for optimal performance).
6. "Dockerfile": contains instructions for docker to work (building/running program with the requirements, api, jobs, and worker files).
7. "docker-compoase.yml":  containerized docker commands (for automation purposes).
8. "data/": an empty data folder (includes a .gitcanary file to post the relatively empty data/ folder to GitHub). Redis database writes a dump.rdb file to this folder. Empty data/ folder is created for correct write permissions. 
9. "README.md": this file, describes the functionality of the cardiovascular disease app.

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#implementation)
#  Implementation

## To Build Image
1. Clone this repository:
```bash
git clone git@github.com:rx9933/COE-332-Homework.git
```
2. Navigate to this directory (homework07). 
3. To run program:
```bash
docker-compose up -d
```
Leave the program running while proceeding with Making Requests to Container. Only use "To stop program" when done interacting with app.

4. To stop program:
```bash
docker-compose down
```

## To Make Requests to Running Container
Note: Proceed only if "To Build Image" is complete and the app is running (step 3). 
The following are various curl commands/routes that can be utilized: 

1. To add data to Redis:
```bash
  curl localhost:5000/data -X POST
```
This will return:
```bash
  Data posted successfully
```
2. To retrieve data from Redis:
```bash
  curl localhost:5000/data -X GET
```
This should return a long list of dictionaries of cardiovascular data.

3. To delete data from Redis:
```bash
  curl localhost:5000/data -X DELETE
```
This should return:
```bash
  Data deleted successfully
```
*Note*: Data on Redis is required for any data analysis; that is how the worker.py gets the data as input. As such, data deletion is not advised to be performed before adding/curling job requests. Doing so will result in empty/uninteresting results as output. 

4.  To add a job:
```bash
  curl localhost:5000/jobs/<"abc"> -X POST -d '{"parameter key 1": "input data 1", "parameter key 2": "input data 2"}' -H "Content-Type: application/json"
```
"abc" should be replaced with a specific worker.py function name, based on the functionality desired of the particular job. View below (Functions section) for more details. 
The dictionary containing "parameter key 1" and "parameter key 2" is a dictionary of any size (based on the required information for the specific worker.py function). 
The job's details (including a job-specific, unique ID) will be returned as a dictionary after the job is posted. 
*NOTE*: ensure that the input dictionary is of strings; both the keys and values *must* be strings.

5. To return information about a specific job:
```bash
  curl localhost:5000/jobs/<"specific_job_id"> -X GET
```
"specific_job_id" should be replaced with the desired job ID. View "To add a job" and "To list all existing jobs" for information on retrieving specific job IDs. 

6. To list all existing jobs (IDs):
```bash
  curl localhost:5000/jobs -X GET
```
Returns a list of all job IDs that have been submitted, are in-progress, or are completed. 

7. To remove all jobs that have not begun (leaves only complete or in-progress jobs):
```bash
  curl localhost:5000/jobs/delete -X DELETE
```
8. To return all the topics of the cardiovascular diseases:
```bash
  curl -X POST -H "Content-Type: application/json" -d '{}' localhost:5000/jobs/return_topics
```
*Note*: no input parameters are required for this command (as represented by the empty input dictionary "{}").
return_topics is the function name in the worker.py file. 
9. To return all data between two years:
```bash
  curl -X POST -H "Content-Type: application/json" -d '{"start":"10", "end":"1990"}' localhost:5000/jobs/return_year_data
```
Start represents the starting year of the data and end represents the ending year. 

## Functions
There are different job functionalities available, based on which worker.py function is called by the user. Currently, the list of job functions are: 
1. return_topics(): returns the major topics of the category Cardiovascular Diseases. Does not require any parameters (input an empty dictionary {})
   An example curl route (job) would be:
  ```bash
  curl localhost:5000/jobs/return_topics -X POST -d '{}' -H "Content-Type: application/json"
  ```
  This would return:
  ```bash
  {
    "function_name": "return_topics",
    "id": "f7125441-ffd6-4489-b6fa-6228a04cd5b4",
    "input_parameters": {},
    "status": "submitted"
  }
  ```
  To get the status of the job (via step 2 of ## To Make Requests to Running Container):
  ```bash
  curl localhost:5000/jobs/f7125441-ffd6-4489-b6fa-6228a04cd5b4 -X GET
  ```
  There are four scenarios in this case:
  1. if the calculation has not started, the command will return:
  ```bash
  {
    "function_name": "return_topics",
    "id": "f7125441-ffd6-4489-b6fa-6228a04cd5b4",
    "input_parameters": {},
    "status": "submitted"
  }
  ```
  2. if the calculation is in progress, the command will return:
  ```bash
  {
    "function_name": "return_topics",
    "id": "f7125441-ffd6-4489-b6fa-6228a04cd5b4",
    "input_parameters": {},
    "status": "in progress"
  }
  ```
  3. if there is no data in the Redis database, the following result will be output:
  ```bash
  {
    "function_name": "return_topics",
    "id": "f7125441-ffd6-4489-b6fa-6228a04cd5b4",
    "input_parameters": {},
    "result": [],
    "status": "complete"
  }
 ```
 3. if data has been correctly loaded, the following result should be output:
 ```bash
 {
  "function_name": "return_topics",
  "id": "7a583722-95be-4f94-a540-2a2397cd3847",
  "input_parameters": {},
  "result": [
    "Stroke",
    "Acute Myocardial Infarction (Heart Attack)",
    "Major Cardiovascular Disease",
    "Coronary Heart Disease"
  ],
  "status": "complete"
}
 ```
2. return_year_data(): returns all data between two input years. Note that data is not sorted when output.
   To post the job:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"start":"10", "end":"1990"}' localhost:5000/jobs/return_year_data
   ```
   To get the status of the job (via step 2 of ## To Make Requests to Running Container):
  ```bash
  curl -X GET localhost:5000/jobs/1f4c5709-322b-4407-891f-79f650cfa780
  ```
  If there is no data between the start and end (between year 10 and year 1990, in this case), the following will be output:
  ```bash
  {
    "function_name": "return_year_data",
    "id": "1f4c5709-322b-4407-891f-79f650cfa780",
    "input_parameters": {
      "end": "1990",
      "start": "10"
    },
    "result": {},
    "status": "complete"
  }
  ```
  Otherwise, data will be output as a set of dictionaries to the screen. 
  *Note*: as mentioned above, this function will also return no interesting output (empty) if the data has not been loaded to redis. 
3. test_work(): simulates work by sleeping for 20 seconds, then returns an arbitrary output message that work has been finished. This function does not require the cardiovascular data. As such data in the Redis database is not used.
  Another example curl route (job) would be:
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{}' localhost:5000/jobs/test_work
  ```
To get the status of the job (via step 2 of ## To Make Requests to Running Container):
  ```bash
  curl localhost:5000/jobs/bb17f28c-5def-48f8-b791-9a11d76f1129 -X GET
  ```
  where "bb17f28c-5def-48f8-b791-9a11d76f1129" is the job id. 
  There are three scenarios in this case:
  1. if the calculation has not started, the command will return:
```bash
   {
    "function_name": "test_work",
    "id": "bb17f28c-5def-48f8-b791-9a11d76f1129",
    "input_parameters": {},
    "status": "submitted"
  }
```
  2. if the calculation is in progress:
```bash
  {
    "function_name": "test_work",
    "id": "bb17f28c-5def-48f8-b791-9a11d76f1129",
    "input_parameters": {},
    "result": {},
    "status": "in progress"
  }
```
  3. if the calculation is complete:
   ```bash
  {
    "function_name": "test_work",
    "id": "bb17f28c-5def-48f8-b791-9a11d76f1129",
    "input_parameters": {},
    "result": {
      "random output parameter 1": "1st output parameter value"
    },
    "status": "complete"
  }
  ```  

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
2. For incorrect job calls when adding a new job (incorrect parameters are input):
   For the return_year_data route:
   Generally, the following error will be output if the input parameters are input incorrectly:
   ```bash
       {
      "error": "Invalid input. Please provide 'start' and 'end' as strings of integers. For example {'start':'1999', 'end':'2000'}"
        }
   ```
   If the following errors occur, view the example of return_year_data route (the spelling of the input data is still likely incorrect):
   1.
```bash
  curl: (3) URL using bad/illegal format or missing URL
```
  2.
```bash
   obs/return_year_data
  <!doctype html>
  <html lang=en>
  <title>400 Bad Request</title>
  <h1>Bad Request</h1>
  <p>Failed to decode JSON object: Expecting &#39;,&#39; delimiter: line 1 column 25 (char 24)</p>
```

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#contributions)
#  Contributions
* Arushi Sadam on app development and writing the Readme.
* Alana Gaughan on developing the environment variable code.
* Professor Joe Allen: on providing immediate help for all my questions.
* [COE 332: Software and Engineering Design Read The Docs](https://coe-332-sp24.readthedocs.io/en/latest/unit05/containers_2.html): on usage (running the program with Linux commands)
* [CDC: National Cardiovascular Disease Surveillance Data)](https://data.cdc.gov/Heart-Disease-Stroke-Prevention/Behavioral-Risk-Factor-Surveillance-System-BRFSS-N/ikwk-8git/about_data): on providing data.
* ChatGPT: on writing this README.md.
