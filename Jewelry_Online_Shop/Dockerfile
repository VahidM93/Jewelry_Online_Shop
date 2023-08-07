FROM python:3.11.1
LABEL version="1.1"
LABEL owener="Vahid"
WORKDIR /app
COPY requirments.txt .
RUN pip install -U pip
RUN pip install -r requirments.txt
COPY . .
EXPOSE 8000
CMD [ "python","manage.py","runserver","0.0.0.0:8000" ] 