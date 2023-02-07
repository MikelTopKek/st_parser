build:
	docker-compose -f docker-compose.yml build ;

start_filling_data:
	docker-compose run --rm web python run.py filling_data
	cat results.txt

start_optimal_items:
	docker-compose run --rm web python run.py optimal_items
	cat results.txt

start_best_airship_item:
	docker-compose run --rm web python run.py best_airship_item
	cat results.txt

start_best_blue_seven_item:
	docker-compose run --rm web python run.py blue_seven_item
	cat results.txt

start_clothes_items:
	docker-compose run --rm web python run.py clothes_items
	cat results.txt

best_craft:
	docker-compose run --rm web python run.py best_craft
	cat results.txt

start_meals_items:
	docker-compose run --rm web python run.py meals_items
	cat results.txt

get_blueprints:
	docker-compose run --rm web python run.py get_blueprints

confirm_blueprints:
	docker-compose run --rm web python run.py confirm_blueprints

start_db:
	docker-compose -f docker-compose.yml up -d db;

stop:
	docker-compose -f docker-compose.yml stop;

down:
	docker-compose -f docker-compose.yml down;

help:
	$(info $(HELP))
	@echo


define HELP
Don`t forget to create and config your .env file!

Build containers:
make build

Start database container:
make start_db

Fill db with data:
make start_filling_data

Get best items to levelling up (best index cost/exp):
make start_optimal_items

Get cheapest flawless and better item 7+ tier, which selling for gold:
make start_best_blue_seven_item

Get best items with highest airship_power of your tier:
make start_best_airship_item

Get best clothes to get exp to tailor
start_clothes_items

Get best clothes to get exp to cook
start_meals_items

Get best item to craft to sell on market
best_craft

Get .csv with blueprints where you can write blueprints, which you have
get_blueprints

Confirm your blueprints
confirm_blueprints

Stop containers:
make stop

Down containers:
make down

Get all make commands:
make help
endef
