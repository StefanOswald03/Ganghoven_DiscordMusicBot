FROM python:3.11
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "./main.py" ]
