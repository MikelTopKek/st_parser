current_dir = $(shell pwd)

build:
	docker-compose -f docker-compose.yml build ;

start:
	docker-compose -f docker-compose.yml up web;

start_db:
	docker-compose -f docker-compose.yml up db;
