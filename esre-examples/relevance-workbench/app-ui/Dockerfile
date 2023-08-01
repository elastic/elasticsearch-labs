FROM node:16-alpine as dependencies
WORKDIR /app-ui
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

FROM node:16-alpine as runner
WORKDIR /app-ui
# ENV NODE_ENV production
COPY next.config.js ./
COPY public ./public
COPY src ./src
COPY jsconfig.json ./jsconfig.json
COPY next.config.js ./next.config.js
COPY jsconfig.json ./jsconfig.json
COPY postcss.config.js ./postcss.config.js
COPY tailwind.config.js ./tailwind.config.js
COPY --from=dependencies /app-ui/node_modules ./node_modules
COPY package.json ./package.json
COPY entrypoint.sh .

# Execute script
RUN apk add --no-cache --upgrade bash
RUN apk add --no-cache --upgrade curl
## RUN apk add --no-cache ripgrep

RUN ["chmod", "+x", "./entrypoint.sh"]
ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 3000
CMD ["yarn", "dev"]
