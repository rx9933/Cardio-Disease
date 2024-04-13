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
   "functionName" should be replaced with a specific worker.py function name, based on the functionality desired for the particular job. View below (Functions          section) for more details and example jobs. The dictionary containing "parameter key 1" and "parameter key 2" is a dictionary of any size (based on the             required information for the specific worker.py function). The job's details (including a job-specific, unique ID) will be returned as a dictionary after the       job is posted.*Note*: ensure that the input dictionary is of strings; both the keys and values must be strings.
  


    
