FROM node:20-slim
WORKDIR /app
COPY package.json /app/package.json
COPY vite.config.js /app/vite.config.js
RUN npm install
COPY src /app/src
COPY index.html /app/index.html
ENV VITE_API_BASE_URL=http://localhost:8080/api
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
