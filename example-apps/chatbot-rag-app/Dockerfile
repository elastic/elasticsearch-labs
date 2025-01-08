FROM node:22-alpine AS build-step
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

# Default to disabling instrumentation, can be overridden to false in
# docker invocations to reenable.
ENV OTEL_SDK_DISABLED=true

# https://github.com/elastic/genai-instrumentation/issues/255
# Currently Python SDK has a bug that spams logs when opentelemetry-instrument is used
# with SDK being disabled. Until it is fixed, we handle it in our own entrypoint by
# avoiding opentelemetry-instrument when SDK is disabled.
RUN echo 'if [ "${OTEL_SDK_DISABLED:-true}" == "false" ]; \
  then \
    opentelemetry-instrument $@; \
  else \
    exec $@; \
  fi' > entrypoint.sh
ENTRYPOINT [ "bash", "-eu", "./entrypoint.sh" ]
CMD [ "python", "api/app.py"]
