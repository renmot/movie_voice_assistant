FROM python:3.9
 
WORKDIR /opt/app/

COPY ./requirements.txt requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app .
 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]