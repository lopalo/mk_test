# mk_test

#### Installation and running

- Install Docker and Docker Compose
- cd mk_test
- Build containers: ./scripts/build_server_container && ./scripts/build_frontend_container
- Compile JS: ./scripts/compile_js 
- docker-compose up -d
- Page URL: localhost:9080/live.html
- Run test: docker-compose run test
