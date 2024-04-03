import requests 
import redis
from flask import Flask, request
from jobs import add_job, get_job_by_id, get_all_job_ids, rd, delete_jobs

app = Flask(__name__)

@app.route('/jobs', methods=['GET'])
def all_jobs():
    all_job_ids = get_all_job_ids()
    return all_job_ids

@app.route('/jobs/<functName>', methods=['POST'])
def submit_job(functName):
    data = request.get_json()
    job_dict = add_job(functName, data)
    return job_dict

@app.route('/jobs/<jobid>', methods=['GET'])
def get_job(jobid):
    result = get_job_by_id(jobid)
    if result == "error":
        return "job does not exist (never was placed on queue) or has been deleted. \n"
    return result

@app.route('/jobs/delete', methods = ["DELETE"])
def delete_all_jobs():
    delete_jobs()
    return "all jobs have been deleted off of worker queue. \n"

@app.route('/data', methods= ['GET', 'POST', 'DELETE'])
def edit_redis_data():
    '''
    Edits the redis database. 
    If method = POST, Posts the data into the redis data base
    If method = GET, Returns all data in the db, 
        Outputs: return_list (list), list of dictionaries containing all data in the db
    if method = DELETE, Deletes all data from db
    '''
    rd = get_redis_client()
    if request.method == 'POST':
        response = requests.get(url="https://data.cdc.gov/resource/ikwk-8git.json")
        data = response.json()
        for row in data:
            # Adding the data to redis as a hash with teh key being teh row id
            row_id = str(row['row_id'])
            rd.hset(row_id, mapping=row)
        return "Data posted successfully"
    if request.method == 'GET':
        return_list = []
        for key in rd.keys():
            key_data = rd.hgetall(key)
            return_list.append(key_data)
        return return_list
    if request.method == 'DELETE':
        rd.flushdb()
        return "Data deleted successfully"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
