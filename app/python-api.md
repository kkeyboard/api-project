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
```
uvicorn app.api:app \ # location of app
--host 0.0.0.0 \      # localhost
--port 8010 \       
--reload \              # reload every time we update
--reload-dir tagifai \  # only reload on updates to 'tagifai' directory
--reload-dir app        # and the app directory
```
- Notice that we only reload on changes to specific directories, as this is to avoid reloading on files that won't impact our application such as log files, etc.
- If we want to manage multiple uvicorn workers to enable parallelism in our application, we can use Gunicorn in congunction with Uvicorn. This will usually be done in a production environment where we will be dealing with meaningful traffic. We have included a app/gunicorn.py script with the customizable configuration and we can launch all the workers with the following command:
  - `gunicorn -c config/gunicorn.py -k uvicorn.workers.UvicornWorker app.api:app`
- We will add both of these commands to our README.md file as well:
```
uvicorn app.api:app --host 0.0.0.0 --port 8010 --reload --reload-dir tagifai --reload-dir app  # dev
gunicorn -c app/gunicorn.py -k uvicorn.workers.UvicornWorker app.api:app  # prod
```

### Requests
- Now that we have our application running, we can submit our GET request using several different methods:
- Visit the endpoint on a browser at http://localhost:8010/
- `curl -X GET http://localhost:8010/`
- Access endpoints via code. Here we show how to do it with the requests library in Python but it can be done with most popular languages.
```python
import json
import requests

response = requests.get("https://localhost:8010/")
print(json.loads(response.text))
```
- Using external tools like Postman, which is great for managed tests that you can save and share with other, etc.
- For all of these, we will see the exact same response from our API:
```
{
  "message": "OK",
  "status-code": 200,
  "data": {}
}
```
#### Using the Request Directly
- Up to now, you have been declaring the parts of the request that you need with their types.
- Taking data from:
  - The path as parameters
  - Headers
  - Cookies
  - etc
- And by doing so, FastAPI is validating that data, converting it and generating documentation for your API automatically. But there are situations where you might need to access the Request object directly.
- As FastAPI is actually Starlette underneath, with a layer of serveral tools on top, you can use Starlette's Request object directly when you need to.
- If would also mean that if you get data from the Request object directly, it won't be validated, converted or documented by FastAPI.
- But there are specific cases where it is useful to get the Request objct:
  - Imagine you want to get the client's IP address/host inside of your path operation function.
  - For that you need to access the request directly.
```python
from fastapi import FastAPI, Request
app = FastAPI()

@app.get("/items/{item_id}")
def read_root(item_id: str, request: Request):
    client_host = request.client.host
    return {"client_host": client_host, "item_id": item_id}
```
- By declaring a path operation function parameter with the type being the Request FastAPI will know to pass the Request in that parameter.

### Decorators
- In our GET \ request's response above, there was not a whole lot of information about the actual request, but it's useful to have details such as URL, timestamp, etc. 
- But we don't want to do this individually for each endpoint. So let's use decorator to automatically add relevant metadata to our response.
```python
# app/api.py
from datetime import datetime
from functools import wraps
from fastapi import FastAPI, Request

def construct_response(f):
  @wrap(f)
  def wrap(request: Request, *args, **kwargs) -> Dict:
      results = f(request, *args, **kwargs)
      response = {
        "message": results["message"],
        "method": request.method,
        "status-code": results["status-code"],
        "timestamp": datetime.now().isoformat(),
        "url": request.url._url,
      }
      if "data" in results:
          response["data"] = results["data"]
      return response

    return wrap
```
- We are passing in a Request instance so we can access information like the request method and URL.
- Therefore, our endpoint functions also need to have this Request object as an input argument. Once we receive the results from our endpoint function f, we can append the extra details and return a more informative response.
- To use this decorator, we just have to wrap our functions accordingly.
```python
@app.get("/")
@constructor_response
def _index(request: Request) -> Dict:
    # Health check
    response = {
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
        "data" {},
    }
    return response
```
- The response:
```json
{
    message: "OK",
    method: "GET",
    status-code: 200,
    timestamp: "2021-02-08T13:19:11.343801",
    url: "http://localhost:8000/",
    data: { }
}
```
- There are also some built-in decorators we should be aware of. We have already seen the path operation decorator(@app.get("/")) which defines the path for the endpoint as well as other attributes.
- There is also the events decorator(@app.on_event()) which we can use to startup and shutdown our application. 
- For example, we use the @app.on_event("startup") event to load the artifacts for the model to use for inference. The advantage of doing this as an event is that our service won't start until this is complete and so no requests will be prematurely processed and cause errors. 
- Similarly, we can perform shutdown events with @app.on_event("shutdown") such as saving logs, cleaning, etc.
```python
from pathlib import Path
from config import logger
from tagifai import main

@app.on_event("startup")
def load_artifacts():
    global artifacts
    run_id = open(Path(config.CONFIG_DIR, "run_id.txt")).read()
    artifacts = main.load_artifacts(model_dir=config.MODEL_DIR)
    logger.info("Ready for inference")
```

#### Lifespan Events
- You can define logic that should be executed before the application starts up. This means that this code will be executed once, before the application starts receiving requests.
- The same way, you can define logic that should be executed when the application is shutting down. In this case, this code will be executed once, after having handled possibly many requests.
- Because this code is executed before he application starts taking requests, and right after it finishes handling requests, it covers the whole application lifespan.
- This can be very useful for setting up resources that you need to use for the whole app, and that are shared among requests, and/or that you need to clean up afterwards.
- For example, a database connection pool, or loading a shared machine learning model.
- Imagine that you have some machine learning models that you want to use to handle requests. The same models are shared among requests, so it is not one model per request, or one per user or someting similar. Imagine that loading the model can take quite some time, because it has to read a lot of data from disk. So you don't want to do it for every request.
- You could load it at the top level of the module/file, but that would also mean that it would load the model even if you are just running a simple automated test, then that test would be slow because it would have to wait for the model to load before being able to run an independent part of the code.
- That's what we will solve, let's load the model before the requests are handled, but only right before the application starts receiving requests, not while the code is being loaded.
- You can define this startup and shutdown logic using the lifespan parameter of the FastAPI app, and a context manager.
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

def fake_answer_to_everything_ml_model(x: float):
  return x*32

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
  ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
  yield
  ml_models.clear()

app = FastAPI(lifespan=lifespan)

@app.get("/predict")
async def predict(x: float):
  result = ml_models["answer_to_everything"](x)
  return {"result":result}
```
- Here we are simulating the expensive startup operation of loading the model by putting the model function in the dictionary with machine learning models before the yield. This code will be executed before the application starts taking requests, during the startup.
- And the, right after yield, we unload the model. This code will be executed after the application finishes handling requests, right before the shutdown. This could, for example, release resources like memory or a GPU.
- Lifespan function:
  - The first thing to notice, is that we are defining an async function with yield. This is very similar to Dependencies with yield.


#### Concurrency and async/await
- Details about the async def syntax for path operation functions and some background about asynchronous code, concurrency and parallelism.
- Summary:
  - If you are using third party libraries that tell you to call them with await:
    - `results = await some_library()`
  - Then declare your path operation functions with async def.
  - You can only use await inside of functions created with async def.
```python
@app.get('/')
async def read_results():
    results = await some_library()
    return results
```
  - If you are using a third party library that communicates with something(a database, an API, the file system, etc) and doesn't support for using await, (this is currently the case for most database libraries), then declare your path operation functions as normally, with just def,
```python
@app.get('/')
def results():
    results = some_library()
    return results
```
  - If your application doesn't have to communicate with anything else and wait for it to respond, use async def.
  - If you just don't know, use normal def.

##### Asynchronous code
- Modern versions of Python have support for asynchronous code using something called coroutines with async and await syntax.
- Asynchronous code means that the language has a way to tell the computer that at some point in the code, it will have to wait for something else to finish somewhere else.
- Let's call that something else is called slow-file. Durint that time, the computer can go and do some other work, while slow-file finishes.
- Then the computer will come back every time it has a chance necause it's waiting again, or whenever it finished all the work it had at that point. And it will see if any of the tasks it was waiting for have already finished, doing whatever it had to do.
- That wait for something else normally refers to I/O operations that are relatively slow compared to the speed of the processor and the RAM memory, like waitinf for:
  - The data from the client to be sent through the network
  - The data sent by your program to be received by the client through the network.
  - The contents of a file in the disk to be read by the system and given to your program
  - The contents your program gave to the system to be written to disk
  - A remote API operation
  - A database operation to finish
  - A database query to return the results
- The execution time is consumed mostly by waiting for I/O operations, they call them I/O bound operations.
- It's called asynchronous because the computer doesn't have to be synchronized with the slow task, waiting for the exact moment that the task finishes, while doing nothing, to be able to take the task result and continue the work.
- Instead of that, by being an asynchronous system, once finished, the task can wait in line a little bit for the computer to finish whatever it went to do, and then come back to take the results and continue working with them.
- For synchronous they commonly also use the term sequential because the computer follows all the steps in sequence before switching to a different task, even if those steps involve waiting.
- The idea of asynchronous code described above is also sometimes called concurrency. It is different from parallelism.
- Concurrency and parallelism both relate to different things happening more or less at the same time. But the details between concurrency and parallelism are quite different.
- In case of most of the web applications:
  - There are many users but your server is waiting for their not-so-good connection to send their requests.
  - And then waiting again for the responses to come back.
  - The waiting is measured in microseconds, but still, summing it all, it is a lot of waiting in the end.
  - That's why it makes a lot of sense to use asynchronous code for web APIs.
  - This kind of asynchronicity is what made NodeJS popular(even though NodeJS is not parallel) and that's the strength of Go as a programming language. And that's the same level of performance you get with FastAPI.
- You can have parallelism and asnychronicity at the same time, you get higher performance than most of the tested NodeJS framework and on par with Go, which is a compiled language closer to C.
- Concurrency is different than parallelism. And it is better on specific scenarios that involve a lot of waiting. Because of that, it generally is a lot better than parallelism for web application development. But not for everything.
- As most of the execution time is taken by actual work(instead of waiting), and the work in a computer is done by a CPU, they call these problems CPU bound.
- Common examples of CPU bound operations are things that require complex math processing:
  - Audio or image processing
  - Computer vision: an image is composed of millions of pixels, each pixel has 3 values/colors, processing that normally requires computing something on those pixels, all at the same time.
  - Machine learning: It normally requires lots of matrix and vector multiplications. 
  - Deep learning: This is a sub-field of machine learning.
- With FastAPI, you can take the advantage of concurrency that is very common for web development. But you can also exploit the benefits of parallelism and multiprocessing for CPU bound workloads like those in machine learning systems.

##### async and await
- When there is an operation that will require waiting before giving the results and has support for these new Python features, you can does it like:
  - `burgers = await get_burger(2)`
- The key is await. It tells Python that it has to wait for get_burgers(2) to finish doing its thing before storing the results in burgers. With that, Python will know that it can go and do something else in the meanwhile.
- For await to work, it has to be inside a function that supports this asynchronicity. To do that, you just declare it with async def:
```python
async def get_burgers(number: int):
    # Do something
    return burgers

```
- With async def, Python knows that, inside that function, it has to be aware of await expression, and that it can pause the execution of that function and go do something else before coming back.
- When you want to call an async def function, you have to await it. So this won't work:
  - `burgers = get_burgers(2)`
- So if you are using a library tells you that you can call it with await, you need to create the path operation functions that uses it with async def, like in:
```python
@app.get('/burgers')
async def read_burgers():
    burgers = await get_burgers(2)
    return burgers
```
- You might have noticed that await can only be used inside of functions defined with async def. But at the same time, functions defined with async def have to be awaited. So, functions with async def can only be called inside of functions defined with async def too.
- So about the egg and the chicken, how do you call the first async function? If you are working with FastAPI you don't have to worry about that, because that first function will be your path operation function, and FastAPI will know how to do the right thing.
- But if you want to use async/await without FastAPI, you can do it as well.

##### Coroutines
- Coroutines is just the very fancy term for the thing returned by an async def function. Python knows that it is something like a function that it can start and that it will end at some point, but that it might be paused internally too, whenever there is an await inside of it.
- But all this functionality of using asynchronous code with async with await is many times summarized as using coroutines. It is comparable to the main key feature of Go, the Goroutines.

##### Extra technical details
- When you declare a path operation function(e.g. @app.get('/')) with normal def instead of async def, it is run in an extrenal threadpool that is then awaited, instead of being called directly (as it would block the server).
- 






### Documentation
- When we define an endpoint, FastAPI automatically generate some documentation based on the its inputs, typing, outputs, etc.
-  We can access Swagger UI for our documentation by going to /doc endpoints on any browser while the api is running.
-  Click on an endpoint Try it out > Execute to see what the server's response will look like. Since this was a GET request without any inputs, our request body was empty but for other method's we will need to provide some information.
-  Notice that our endpoint is organized under sections in the UI. We can use tags when defining our endpoints in the script:
```python
@app.get("/", tags=["General"])
@construct_response
def _index(request: Request) -> Dict:
    # Healther check
    response = {
        "message": HTTPStatus.OK.phrase,
        "status-code": HTTPStatus.OK,
        "data": {},
    }
    return response
```
- You can also use /redoc endpoint to view the ReDoc documentation or Postman to execute and manage tests that you can save and share with others.

## Resources

## Product

## Model server