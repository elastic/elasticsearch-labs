FROM node:22-alpine

ENV NODE_ENV production
WORKDIR /usr/src/app
COPY . .
RUN --mount=type=cache,target=/root/.npm \
    npm install --omit=dev
USER node
EXPOSE 3000

# Default to disabling instrumentation, can be overridden to false in
# docker invocations to reenable.
ENV OTEL_SDK_DISABLED=true

ENTRYPOINT ["npm", "run"]
CMD ["app"]
