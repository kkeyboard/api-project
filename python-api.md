# APIs

## Intuition
- There are several limitations to serving our models with CLI:
  - Users need access to the terminal, codebase, virtual environment, etc.
  - CLI outputs on the terminal are not exportable
- To address these issues, we are going to develop an application programming interface that will anyone to interact with our application with a simple request.
- The end user may not directly interact with our API but may use UI/UX components that send requests to ours.

## Serving
- APIs allow different applications to communicate with each other in real-time. But when it comes to serving predictions, we need to first decide if we will do that in batches or real-time, which is entirely based on the feature space(finite vs unbound).

### Batch serving
- We can make batch predictions on a finite set of inputs which are then written to a database for low latency inference. When a user or downstream process sends an inference request in real-time, cached results from the database are returned.
- pros:
  - Generate and cache predictions for very fast inference for users.
  - The model doesn't need to be spun up as it's own service since it is never used in real-time.
- cons:
  - Predictions can become stale if user develops new interests that aren't captured by the old data that the current predictions are based on.
  - Input feature space must be finite because we need to generate all the predictions before they are needed for real time.
- What are some tasks where batch serving is ideal?
  - Recommended content that existing users will like based on their viewing history. However, new users may just receive some generic recommendations based on their explicit interests until we process their history the next day. And even if we are not doing batch serving, it might still be useful to cache very popular sets of input features(ex. combination of explicit interests leads to certain recommended content) so that we can serve those predictions faster.

### Real-time serving
- We can also serve live predictions, typically through a request to an API with the appropriate input data.
- pros:
  - Can yield more up-to-date predictions which may yield a more meaningful user experience, etc.
- cons:
  - Requires managed microservices to handle request traffic.
  - Requires real-time monitoring since input space is unbounded, which could yield erroneous predicitons.
- In this lesson, we will create the API required to enable real-time serving. The interactions in our situation involve the client(users, other applications, etc) sending a request(ex. prediciton request) with the appropriate inputs to the server(our application with a trained model) and receiving a response(ex. prediction) in return.


## Request
- Users will interact with our API in the form of a request. 

### URI
- A uniform resource identifier(URI) is an identifier for a specific resource.
    - `https://localhost:8000/models/{modelId}/?filter=passed#detail`
- scheme: protocol definition
  - https://
- domain: address of website
  - localhost
- port: endpoint
  - :8000
- path: location of the resource
  - /models/{modelId}/
- query string: parameters to identify resources
  - ?filter=passed
- anchor: location on webpage
  - #details

### Method
- The method is the operation to execute on the specific resource defined by the URI. 
- There are many possible methods to choose from, but the four below are the most popular, which are often referred to as CRUD because they allow you to Create, Read, Update and Delete.
  - GET: get a resource
  - POST: create or update a resource
  - PUT/PATCH: create or update a resource
  - DELETE: delete a resource
- You could use either the POST or PUT request method to create and modify resources but the main difference is that PUT is idempotent which means you can call the method repeatedly and it will produce the same state every time. Whereas, calling POST multiple times can result in creating multiple instance and so changes the overall state each time.
```bash
POST /models/<new_model> -d {} # Error since we haven't created the new_model resource yet
POST /modes -d {} # Creates a new model based on information provided in data
POST /models/<existing_model> -d {} # Updates an existng model based on information provided in data.

PUT /models/<new_model> -d {} # Create a new model based on information provided in data
PUT /models/<existing_model> -d {} # Updates an existing model based on information provided in data.

```
- We can use cURL to execute our API calls.
```bash
curl -X #HTTP method
curl -H # headers to be sent to the request(ex. authenticaion)
curl -d <data> # HTTP POST data

curl -X GET "https://localhost:8000/models"
```

#### cURL RESTful API
- Curl is command-line utility for transferring data to or from a remote server. Curl is used for API testing, sending files to the server, and viewing the server response headers.
- Curl supports over 25+ protocols, including HTTP, HTTPS, FTP, FTPS, and SFTP, has built-in support for SSL certificates, HTTP cookies, and more.
- The term REST stands for representational state transfer. It is an architectural style that consists of a set of constraints to be used when creating web services.
- RESTful API is an API that follows the REST architecture. Typically REST APIs use the HTTP protocol for sending and retrieving data and JSON formatted responses. You can use the standard HTTP methods to create, view, update, or delete resources through the API.
- To test and interact with the RESTful APIs, you can use any library or tool that can make HTTP requests.

- API requests are made up for four different parts:
  - The endpoint: This is the URL that the client uses to communicate with the server.
  - The HTTP method: It tells the server what action the client wants to perform. The most common methods are GET, POST, PUT, DELETE, and PATCH.
  - The headers: Used to pass additional information between the server and the client, such as authorization.
  - The body: The data sent to the server.
  
- Curl options:
  - curl -X [POST, DELETE, ...], --request: The HTTP method to be used.
  - curl -i, --include: Include the response headers.
  - curl -d, --data: The data to be sent.
  - curl -H, --header: Additional header to be sent.
  
- HTTP GET:
  - The GET method requests a specific resource from the server.
  - GET is the default method when making HTTP request with curl.
  - Here is an example of making a GET request to the JSONPlaceholder API to a JSON representation of all posts:
    - `curl https://jsonplaceholder.typicode.com/posts`
  - To filter the results use query params:
    - `curl https://jsonplaceholder.typicode.com/posts?userId=1`

- HTTP POST:
  - The POST method is used to create a resource on the server. If the resource exists, it is overriden.
  - The following command makes a POST request(`-X POST`) using the data specified with the -d option(`-d "userId=5&title=Hello World&body=Post body."`):
    - `curl -X POST -d "userId=5&title=Hello World&body=Post body." https://jsonplaceholder.typicode.com/posts`
- The type of the request body is specified using the Content-Type header. By default when this header is not given curl uses Content-Type: application/x-www-form-urlencoded.
- To send a JSON formatted data set the body type to applications/json:
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"userId": 5, "title": "Hello World", "body": "Post body."} \
https://jsonplaceholder.typicode.com/posts
```

- HTTP PUT:
  - The PUT method is used to update or replace a resource on the server. It replaces all data of the specified resource with the request data.
  - `curl -X PUT -d "userId=5&title=Hello World&body=Post body." https://jsonplaceholder.typicode.com/posts/5`

- HTTP PATCH:
  - The PATCH modifies an existing resources partially.
  - For a PATCH request, we don't need to provide all the data. We only send the data that we want to update.
  - The main difference from the HTTP PUT method is that the HTTP PATCH method partially replaces the resource, while the HTTP PUT method completely replaces the resource.
  - To send a PATCH request using curl, you need to 
    - tell curl to send a PATCH request by specifying the -X PATCH command line switch,
    - pass the PATCH data with the -d command line switch, and
    - provide the correct ContentType HTTP header with command line switch -H.
    - The -X PATCH command line switch tell curl to use the HTTP PATCH method instead of POST.
    - The -H 'Content-Type: application/json' command line switch tells curl to send an HTTP header to the server, indicating the data type in the PATCH message's body.
    - In this example, we send a PATCH request to the ReqBin echo URL. 
      - `curl -X PATCH https://reqbin.com/echo/patch/json -H 'Content-Type: application/json' -H 'Accept: application/json -d '{"Id": 78912, "Customer": "Jason Sweet", "Quantity": 1}'`

- HTTP DELETE:
  - The DELETE method removes the specified resource from the server.
  - `curl -X DELETE https://jsonplaceholder.typicode.com/posts/5`

- Authentication
  - If the API endpoint requires authentication, you will need to obtain the access key. Otherwise, the API server will respond with the Access Forbidden or Unauthorized response message.
  - The process of obtaining an access key depends on the API you are using. Once you have your access token you can send it in the header:
    - `curl -X GET -H "Authorization: Bearer {ACCESS_TOKEN}" "https://api.server.io/posts"`


### Headers
- Headers contain information about a certain event and are usually found in both the client's request as well as the server's response.
- It can range from what type of format they will send and receive, authentication and caching info, etc.
```bash
curl -X GET "http://localhost:8000/" \          # method and URI
    -H  "accept: application/json"  \           # client accepts JSON
    -H  "Content-Type: application/json" \      # client sends JSON`
```

### Body
- The body contains information that may be necessary for the request to be processed. It is usually a JSON object sent during POST, PUT/PATCH, DELETE request methods.
```bash
curl -X POST "http://localhost:8000/models" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d "{'name': 'some_name', ...}

```

## Response
- The response we receive from our server is the result of the request we sent. 
- The response also includes headers and a body which should include the proper HTTP status code as well as explicit messages, data, etc.
```json
{
    "message": "OK",
    "method": "GET",
    "status-code": 200,
    "url": "http://localhost:8000/",
    "data": {}
}
```
- We may also want to include other metadata in the response such as model version, datasets used, etc. Anything that the downstream consumer may be interested in or metadata that might be useful for inspection.
- Common HTTP status code:
  - 200 OK,         method operation was successful.
  - 201 CREATED,    POST or PUT method successfully created a resource.
  - 202 ACCEPTED,   the request was accepted for processing(but processing may not be done).
  - 400 BAD REQUEST,server cannot process the request because of a client side error.
  - 401 UNAUTHORIZED,   you are missing required authentication.
  - 403 FORBIDDEN,      you are not allowed to do this operation.
  - 404 NOT FOUND,      the resource you are looking for was not found.
  - 400 INTERNAL SERVER ERROR,  there was failure somewhere in the system process.
  - 501 NOT IMPLEMENTED,        this operation on the resource doesn't exist yet.

## Best practices
- When we design our API, there are some best practices to follow:
  - URI paths, messages, etc,  should be as explicit as possible. Avoid using cryptic resource names.
  - Use nouns, instread of verbs, for naming resources. The request method already accounts for the verb
    - Good example: GET /users
    - Bad example:  GET /get_users
  - Use plural nouns
    - GET /users/{userId}
  - Use dashes in URIs for resources and path parameters but use underscore for query parameters
    - GET /nlp-models/?find_desc=bert
  - Return appropriate HTTP and informative messages to the user.

## Implementation
- We are going to define our API in a separate app directory because in future, we may have additional packages like tagifai and we don't want our app to be attached to any one package. Inside our app directory, we will create the following scripts:
```bash
mkdir app
cd app
touch api.py gunicorn.py schemas.py
cd ../
```
- api.py: FastAPI app, the main script that will include our API initialization and endpoints.
- gunicorn.py: WSGI script, scripts for defining API worker configurations.
- schemas.py: API model schemas, definitions for the different objects we will use in our resource endpoints.

## FastAPI
- There are plenty of other framework options out there such as Flask, Django and even non-Python based options like Node, Angular, etc. 
- FastAPI combines many of the advantages across these frameworks and is maturing quickly and becoming more widely adopted.
- The advantages are:
  - development in Python
  - highly performant
    - FastAPI provides more features on top of Starlette. Features that you almost always need when building APIs, like data validation and serialization. And by using it, you get automatic documentation for free.
  - data validation via pydantic
    - With Pydantic, schema validation and serialization are controlled by type annotations; less to learn, less code to write, and integration with your IDE and static analysis tools.
    - Pydantic's core validation logic is written in Rust.
    - It can emit JSON schema, allowing for easy integration with other tools.
    - It can run in either strict=True mode(where data is not converted) or strict=False mode where it tries to coerce data to the corret type where appropriate.
    - It supports validation of many standard library types including dataclass and TypedDict.
    - It allows custom validators and serializers to alter how data is processed in many powerful ways.
    - Pydantic Example 1:
        ```python
        from datetime import datetime
        from typing import Tuple
        from pydantic import BaseModel

        class Delivery(BaseModel):
            timestamp: datetime
            dimensions: Tuple[int, int]

        m = Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10', '20'])
        print(repr(m.timestamp))
        print(m.dimensions)
        ```
    - Pydantic Example 2:
```python
from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError

class User(BaseModel):
    # id is of type int; the annotation-only declaration tells Pydantic that this field is required.
    # Strings, bytes, or floats will be coerced to ints if possible; otherwise an exception will be raised.
    id: int 
    # name is string but since it has the default value, it is not required.
    name: str = 'John Doe'
    # signup_ts is a datetime field that is required, but the value None may be provided; Pydantic will process either a unix timestamp int(e.g. 1496498400) or a string representating the date and time.
    signup_ts: datatime | None
    # tastes is a dictionary with string keys and positive integer values. The PositveInt type is shorthand for Annotated[int, annotated_types.Gt(0)]
    tastes: dict[str, PositiveInt]

external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',
    'tastes': {
        'wine': 9,
        b'cheese': 7, # The key is bytes but Pydantic will take care of coercing it to a string.
        'cabbage': '1', # '1' ill be coerced to 1.

    },
}
# Inside a function header:
#   * collects all the positional arguments in a tuple.
#   ** collects all the keyword arguments in a dictionary.
# In a function call:
#   * unpacks a list or tuple into position arguments.
#   ** unpacks a dictionary into keyword arguments.
user = User(**external_data)
print(user.id)
print(user.model_dump())
"""
{
    'id': 123,
    'name': 'John Doe',
    'signup_ts': datetime.datetime(2019, 6, 1, 12, 22),
    'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},
}
"""

# id is not valid integer and signup_ts is missing.
external_data2 = {
    'id': 'not an int',
    'tastes': {}
}

try:
    User(**external_data)
except ValidationError as e:
    print(e.errors())
"""
    [
        {
            'type': 'int_parsing',
            'loc': ('id',),
            'msg': 'Input should be a valid integer, unable to parse string as an integer',
            'input': 'not an int',
            'url': 'https://errors.pydantic.dev/2/v/int_parsing',
        },
        {
            'type': 'missing',
            'loc': ('signup_ts',),
            'msg': 'Field required',
            'input': {'id': 'not an int', 'tastes': {}},
            'url': 'https://errors.pydantic.dev/2/v/missing',
        },
    ]
    """


```
  - autogenerated documentation
  - dependency injection
  - security via OAuth 2
```bash
pip install fastapi==0.78.0
```
- Your choice of framework also depends on your team's existing systems and processes. However, with the wide adoption of microservices, we can wrap our specific application in any framework we choose and expose the appropriate resources so all other systems can easily communicate with it.

### Initialization
- The first step is to initalize our API in our api.py script by defining metadata like the title, description and version:
```python
# app/api.py
from fastapi import FastAPI

app = FastAPI(
    title="TagIfAI - Made With ML",
    description="Classify machine learning projects.",
    version="0.1",
)
```
- Our first endpoint is going to be a simple one where we want to show that everything is working as intended. The path for the endpoint will just be / (when a user visit our base URI) and it will be a GET request. This simple endpoint is often used as a health check to ensure that our application is indeed up and running properly.
```python
from http import HTTPStatus
from typing import Dict

@app.get('/')
def _index() -> Dict:
    # Health check
    response = {
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
        "data": {},
    }
    return response
```
- We let our application know that the endpoint is at / through the path operation decorator and we return JSON response with the 200 OK HTTP status code.

### Launching
- We are using Uviron, a fast ASGI server that can run asynchronous code in a single process to launch our application.
  - `pip install uvicorn==0.17.6`
- We can launch our application with the following command:
```
uvicorn app.api:app \       # location of app(app directory/api.py script/app object)
    --host 0.0.0.0 \        # localhost
    --port 8000 \       
    --reload \              # reload every time we update
    --reload-dir tagifai \  # only reload on updates to 'tagifai' directory
    --reload-dir app        # and the 'app' directory
```
- Notice that we only reload on changes to specific directories, as this is to avoid reloading on files that won't impact our application such as log files, etc.
- If we want to manage multiple uvicorn workers to enable parallelism in our application, we can use Gunicorn in conjunction with Uvicorn. This will be done in a production environment where we will be dealing with meaningful traffic. We've included a app/gunicorn.py script with the customizable configuration and we can launch all the workers with the following command:
```
gunicorn -c config/gunicorn.py -k uvicorn.workers.UvicornWorker app.api:app
```
- We will add both of these commands to our README.md file as well:
```
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload --reload-dir tagifai --reload-dir app  # dev
gunicorn -c app/gunicorn.py -k uvicorn.workers.UvicornWorker app.api:app  # prod
```

### 
