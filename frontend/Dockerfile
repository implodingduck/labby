FROM node:22 as BUILD

WORKDIR /app

COPY src/package.json /app/package.json

RUN ls -lta

RUN npm install 

COPY src /app

RUN npm run build

FROM nginx:alpine

COPY --from=BUILD /app/dist /usr/share/nginx/html

EXPOSE 80
