FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8501

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "Inicio.py", "--server.port=8501", "--server.address=0.0.0.0"]