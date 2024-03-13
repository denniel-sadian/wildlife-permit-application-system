FROM node:19-bullseye-slim as base

# Set working directory
WORKDIR /app

COPY \
    "./package.json" \
    "./package-lock.json" \
    ./
RUN npm install && npm cache clean --force

COPY . .

EXPOSE 5173

CMD npm run dev

# Note: vite.config.js and src code will be mounted via volumes
