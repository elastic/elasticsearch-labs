FROM node:20-alpine AS build-step
WORKDIR /app
ENV PATH=/node_modules/.bin:$PATH
COPY frontend ./frontend
RUN rm -rf /app/frontend/node_modules
RUN cd frontend && yarn install
RUN cd frontend && REACT_APP_API_HOST=/api yarn build

FROM python:3.12-slim

WORKDIR /app
RUN mkdir -p ./frontend/build
COPY --from=build-step ./app/frontend/build ./frontend/build
RUN mkdir ./api
RUN mkdir ./data

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt
COPY api ./api
COPY data ./data

EXPOSE 4000
# The only thing different from running local is that in docker we need to
# listen on all IPs, not just localhost.
ENV FLASK_RUN_HOST=0.0.0.0
CMD [ "flask", "run"]
