# GE Messaging API

GE Messaging API is a simple REST API that allows users to send messages to other users, see messages from a specific sender and see all recent messages.
The API is built on Python, Flask and SqlAlchemy with a SQLite temporary backend database. Please note that data will not persist between separate runnings of the API.

## Steps to install and run
1. Clone the public repository https://github.com/narnold113/ge_messaging_api.git
2. Ensure that docker is installed and the docker daemon is running. See [here] (https://docs.docker.com/config/daemon/)
3. Run the public docker image `narnold113/ge-message-api:latest`
	- `docker run -p 5050:5050 -e IS_DEFAULT_DATA=1 narnold113/ge-message-api:latest`
	- `-e IS_DEFAULT_DATA=1` sets an env var that creates default users and messages on API creation. Omit if you do not want default users and messages
4. GE Messaging API is now running on localhost:5050
5. `ctrl + c` to stop running container

## User Routes/endpoints
- Create User
	- HTTP Method: POST
	- Endpoint: /user
	- Required JSON payload fields:
		- first_name: string
		- last_name: string
		- primary_email: string
- Retrieve User
	- HTTP Method: GET
	- Endpoint: /user
	- Required query params:
		- user_id: string
- Retrieve All Users
	- HTTP Method: GET
	- Endpoint: /users
	- Required query params:
		- None
## Message Routes/endpoints
- Create Message
	- HTTP Method: POST
	- Endpoint: /message
	- Required JSON payload fields:
		- sender_user_id: string
		- recipient_user_id: string
		- message_body: string (max 500 chars)
- Retrieve Message
	- HTTP Method: GET
	- Endpoint: /message
	- Required query params:
		- message_id: string
- Retrieve Messages
	- HTTP Method: GET
	- Endpoint: /messages
	- Required query params:
		- sender_user_id: string (optional)
		- recipient_user_id: string (required if sender_user_id provided)
		- since_date: string (optional, format: MM/dd/yyyy, example: 04/01/2022)
		- limit: integer (optional, defaults to 100)
	- Note
		- If both sender_user_id and recipient_user_id params are excluded in request, response will return all messages
		- If sender_user_id is provided, the recipient_user_id (logged in user making the request) value is required