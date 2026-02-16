## Python concepts

---

**Decorator**

decorators in python extend the functionality of a function


## REST 

---

- is an architectural constraint

### REST constraints

---

- should use the concepts of client and server 

- should be stateless

- should be cacheable

- should use the concept of Resource 

- should have a uniform , hypermedia-driven interface

- if the backend uses multiple servers, this should be invisible to the client

#### what are resources 

- Things that the API deals in

- posts, comments, users, likes etc...

#### what does stateless mean

- stateless means the server doesn't keep information about the clients

- the server doesn't remember previous requests

- being stateless makes the server much simpler, straight forward to code and performant

#### what does hypermedia-driven mean

if a resource is related to another resource, there should be an actual link in the response which allows the client to "find" the related resources

#### what is BaseModel from pydantic

BaseModel is a class in pydantic that allows us to define a Model , and a model is used 

to validate data

#### what is HTTPX

HTTPX is a modern, fully-featured  HTTP client library for python3 that provides both 

synchronous and asnycronouse APIs

#### what is a ficture in pytest 

in pytest, fixtures are functions used to provide a defined , reliable and consistent

environment(or "context") for test to run.

#### what is a generator

In Python, a generator is a special type of function that returns an iterator, and

the ***yield*** keyword is used within the function to produce values one at a time,

pausing execution and saving its state each time. 



