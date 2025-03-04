FROM node:22-alpine AS build-step
WORKDIR /app
ENV PATH=/node_modules/.bin:$PATH
COPY frontend ./frontend
RUN cd frontend && yarn install
RUN cd frontend && REACT_APP_API_HOST=/api yarn build

# Use glibc-based image to get pre-compiled wheels for grpcio and tiktoken
FROM python:3.12-slim

WORKDIR /app
RUN mkdir -p ./frontend/build
COPY --from=build-step ./app/frontend/build ./frontend/build

COPY requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt

RUN mkdir -p ./api ./data
COPY api ./api
COPY data ./data

EXPOSE 4000

# Default to disabling instrumentation, can be overridden to false in
# docker invocations to reenable.
ENV OTEL_SDK_DISABLED=true
ENTRYPOINT [ "opentelemetry-instrument" ]

CMD [ "python", "api/app.py" ]
