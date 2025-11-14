FROM python:3.11-slim

WORKDIR /app

COPY elastic_agent_builder_a2a.py test_elastic_agent_builder_a2a.py ./

RUN pip install agent-framework
RUN pip install python-dotenv

CMD ["python", "-m", "unittest", "test_elastic_agent_builder_a2a.py"]
