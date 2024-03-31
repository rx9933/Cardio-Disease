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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
