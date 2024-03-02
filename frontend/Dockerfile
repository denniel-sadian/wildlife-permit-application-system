FROM node:19-bullseye-slim as base

# Set working directory
WORKDIR /app

COPY . .
RUN npm install && npm cache clean --force

EXPOSE 5173

CMD npm run dev --host

# Note: vite.config.js and src code will be mounted via volumes
