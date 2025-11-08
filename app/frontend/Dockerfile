# Frontend Dockerfile for Vite
FROM node:20-alpine AS build
WORKDIR /app

# Copy only package.json to leverage Docker cache
COPY package.json ./

# Install dependencies based on package.json.
# Yarn is already included in the node:20-alpine image.
RUN yarn install

# Now copy the rest of the application code
COPY . .

# Run the build
RUN yarn build

# Serve static build with nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
