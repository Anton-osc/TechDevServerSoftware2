
# How to start
- Make sure you have installed docker-compose
- Clone this repo
- Run `docker-compose up`
### Calculate Lab3 variant 24 % 3 = 0 - Облік доходів
### Now you can send requests to api:
#### User requests:
- curl -X POST http://127.0.0.1:80/user -H "Content-Type: application/json" -d '{"name": "admin"}' (Create user)
- curl -X GET http://127.0.0.1:80/user/1 (Get user)
- curl -X DELETE http://127.0.0.1:80/user/1 (Delete user)
- curl -X GET http://127.0.0.1:80/users (Get all users)
#### Category requests:
- curl -X POST http://127.0.0.1:80/category -H "Content-Type: application/json" -d '{"name": "products"}' (Create category)
- curl -X GET http://127.0.0.1:80/category/1 (Get category)
- curl -X DELETE http://127.0.0.1:80/category/1 (Delete category)
- curl -X GET http://127.0.0.1:80/category (Get all categories)
#### Record requests:
- curl -X POST http://127.0.0.1:80/record -H "Content-Type: application/json" -d '{"user_id": 1,"category_id": 1,"amount": 150}' (Create record)
- curl -X GET http://127.0.0.1:80/record/1 (Get record)
- curl -X DELETE http://127.0.0.1:80/record/1 (Delete record)
- curl -X GET "http://127.0.0.1:80/record?user_id=1&category_id=1" (Get records for user and category)
