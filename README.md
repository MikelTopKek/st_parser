## Shop Titans parser

You need **git**, **Docker** and **Docker-compose** to run this project.
On Linux-base and MacOS you can use **make** utility to simplify project start.

Core technologies used:
* Postgres
* SQLAlchemy

env folder contains .env file with environmental variables. 

## Fast start
1. Clone project from gitlab with HTTPS or SSH:
   * https://github.com/MikelTopKek/st_parser.git
   * git@github.com:MikelTopKek/st_parser.git

2. Change environment file env/.env

3. Build project

4. Fill db with data

5. Run help to select command you need 

#### If you want to add receipts that you have, you need:
   * Run receipt_changing to create blueprints.csv file
   * Modify column blueprints_availability (1 - you have receipt)
   * Save blueprints.csv


Get available commands:
make help