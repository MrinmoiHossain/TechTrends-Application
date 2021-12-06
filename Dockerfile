FROM python:3.7
LABEL maintainer="Mokit Hossain"

WORKDIR /app
ADD techtrends .

EXPOSE 3111
RUN pip install -r requirements.txt
RUN python init_db.py

CMD ["python", "app.py"]