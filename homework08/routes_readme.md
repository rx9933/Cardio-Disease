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
   
