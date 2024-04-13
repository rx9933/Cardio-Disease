FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt


COPY test/test_api.py test/test_worker.py src/api.py src/worker.py src/jobs.py ./

CMD ["python3"]
