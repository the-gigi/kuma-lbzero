FROM python:3
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8000
ENTRYPOINT hug -f /app/social_graph_reader.py