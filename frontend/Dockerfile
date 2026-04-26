FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# In development, we'll use npm run dev
CMD ["npm", "run", "dev"]
