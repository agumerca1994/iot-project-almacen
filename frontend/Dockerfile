# Construcción del frontend
FROM node:18 AS build
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

# Servidor Nginx para servir React
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
