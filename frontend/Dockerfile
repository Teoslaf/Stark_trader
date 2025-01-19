FROM node:18-alpine

WORKDIR /app

COPY package.json yarn.lock ./
COPY packages/nextjs/package.json ./packages/nextjs/

RUN yarn install

COPY . .

CMD ["yarn", "start"] 