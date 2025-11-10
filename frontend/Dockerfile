# Build stage
FROM node:20-alpine AS builder
WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Runtime stage
FROM nginx:1.27-alpine
COPY --from=builder /usr/src/app/dist /usr/share/nginx/html

# Basic SPA fallback to index.html
RUN printf 'server {\n  listen 80;\n  server_name localhost;\n  root /usr/share/nginx/html;\n  include /etc/nginx/mime.types;\n  index index.html;\n  location / {\n    try_files $uri /index.html;\n  }\n}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
