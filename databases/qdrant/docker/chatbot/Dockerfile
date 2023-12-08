FROM python:3.11-slim-bookworm

ENV QDRANT_URL http://qdrant:6333
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["run","/app/chat.py"]
ENTRYPOINT ["streamlit"]

