FROM node:latest

COPY . /app
WORKDIR /app

RUN npm install -g pnpm
RUN pwd && ls -l && pnpm i && VITE_IMG_FETCH_BASE=/manager pnpm build

FROM nginx:alpine

COPY --from=0 /app/dist /usr/share/nginx/html/
