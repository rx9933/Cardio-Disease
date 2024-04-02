<h1 align="center">Cardiovascular Disease</h1>
<p align="center">
  <b>A containerized Flask-Redis-Kubernetes application that analyzes behavioral risk factors on cardiovascular disease. Final Project for COE332 (Software Engineering and Design).</b></br>
  <sub><sub>
</p>

<br />

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#purpose)
#  Purpose
The project aims to illuminate various correlations between behavioral patterns and cardivascular diseases. The app includes:
1. several endpoints for retrieving specific data subsets, such as by class (cardiovascular rates or risk factors), topic (specific cardiovascular diseases or risk factors), location (states), and breakout category (gender, age, or race)
2. functionality to post, delete, and retrieve data from a Redis database
3. visualizations in graphs.
The app's easy functionality for data visualization allows for widespread access to data patterns and future insights into how lifestyle choices and demographic factors can contribute to cardiovascular health. Ultimately, the app can help inform public health strategies and interventions. 

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#data)
#  Data
Data about various behavioral risk factors (leading to cardiavascular disease) is sourced from the CDC: [National Cardiovascular Disease Surveillance Data)](https://data.cdc.gov/Heart-Disease-Stroke-Prevention/Behavioral-Risk-Factor-Surveillance-System-BRFSS-N/ikwk-8git/about_data). The risk surveillance system is provided by the National Cardiovascular Disease Surveillance System, which integrated multiple indicators from different data sources to create a comprehensive list of Cardiovascular Diseases (CVD) and associated risk factors accross the United States (with around 10 years worth of tracking). Data parameters include year (2011 to 2022), location (national, regional, state, selected sites), indicators (obesity, smoking, etc.), type of CVD (i.e. stroke or heart failure), age group, sex, and race. There are approximately 160,160 data points. Data was last updated August 25th, 2023. Data can be accessed in either a csv or json format; for this project, the app uses the csv data format. 

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
9. "README.md": this file, describes functionality of the cardiovascular diseases app.

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

[![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/cloudy.png)](#contributions)
#  Contributions
* Arushi Sadam and Alana Gaughan on creating the program and README.md file. 
* Professor Joe Allen: on providing immediate help for all my questions.
* [COE 332: Software and Engineering Design Read The Docs](https://coe-332-sp24.readthedocs.io/en/latest/unit05/containers_2.html): on usage (running the program with Linux commands)
* [CDC: National Cardiovascular Disease Surveillance Data)](https://data.cdc.gov/Heart-Disease-Stroke-Prevention/Behavioral-Risk-Factor-Surveillance-System-BRFSS-N/ikwk-8git/about_data): on providing data.
* ChatGPT: on writing this README.md.
