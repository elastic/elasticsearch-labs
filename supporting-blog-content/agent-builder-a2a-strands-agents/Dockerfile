FROM python:3.11-slim

WORKDIR /app

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY elastic_agent_builder_a2a_rps+.py .

CMD ["python", "elastic_agent_builder_a2a_rps+.py"]