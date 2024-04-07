FROM node:latest

COPY . /app
WORKDIR /app

RUN npm install -g pnpm
RUN pwd && ls -l && pnpm i && pnpm build

FROM nginx:alpine

COPY --from=0 /app/dist /usr/share/nginx/html/
