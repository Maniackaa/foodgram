FROM python:3.9
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
#RUN python3 manage.py collectstatic
#RUN mkdir /backend_static
#RUN mkdir /backend_static/static
#RUN cp -r /app/collected_static/. /backend_static/static/
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi"]
#RUN entrypoint.sh
#COPY entrypoint.sh /usr/bin
#RUN python3 manage.py migrate
RUN ["chmod", "+x", "/app/entrypoint.sh"]
ENTRYPOINT ["/app/entrypoint.sh"]