# REST API Tutorial

A comprehensive guide to understanding REST APIs, endpoints, routes, and HTTP fundamentals.

---

## Table of Contents

1. [What REST Actually Is](#what-rest-actually-is)
2. [The Core Idea: Resources](#the-core-idea-resources)
3. [URLs, Endpoints, and Routes](#urls-endpoints-and-routes)
4. [HTTP Methods](#http-methods-the-verbs)
5. [Anatomy of HTTP Request](#anatomy-of-an-http-request)
6. [Anatomy of HTTP Response](#anatomy-of-an-http-response)
7. [Status Codes](#status-codes)
8. [Path Parameters vs Query Parameters](#path-parameters-vs-query-parameters)
9. [Complete Example: Task API](#a-complete-example-task-api)
10. [Common REST Design Patterns](#common-rest-design-patterns)
11. [What's NOT REST](#whats-not-rest)
12. [Quick Reference](#quick-reference)

---

## What REST Actually Is

REST = **Representational State Transfer**

It's not a protocol, library, or framework. It's an **architectural style** - a set of conventions for how clients and servers should communicate.

Think of it like language grammar. Grammar isn't a tool - it's rules everyone agrees to follow so we understand each other. REST is grammar for web APIs.

---

## The Core Idea: Resources

Everything in REST is a **resource**. A resource is any "thing" your application deals with:

- A user
- A task
- A blog post
- An order
- A comment

Each resource has a **unique address** (URL) where it lives:

```
https://api.example.com/users/42
        └── server ──┘   └─ resource path ─┘
```

---

## URLs, Endpoints, and Routes

These terms are related but distinct:

### URL (Uniform Resource Locator)

The complete address:

```
https://api.myapp.com/tasks/15
```

### Endpoint

A specific URL + HTTP method combination that does something:

```
GET  /tasks      ← This is one endpoint
POST /tasks      ← This is a different endpoint (same URL, different method)
GET  /tasks/15   ← This is another endpoint
```

### Route

The **code** that handles an endpoint. When you write backend code, you define routes:

```python
# This is a route definition in FastAPI
@app.get("/tasks")
def list_tasks():
    return all_tasks

@app.post("/tasks")
def create_task(task: Task):
    # save task
    return task
```

### Summary

| Term | Definition |
|------|------------|
| URL | The address |
| Endpoint | Address + method (what clients call) |
| Route | Your code that handles it (what you write) |

---

## HTTP Methods: The Verbs

Each method has a **semantic meaning** - a promise about what it does:

| Method | Purpose | Safe? | Idempotent? |
|--------|---------|-------|-------------|
| GET | Read data | Yes | Yes |
| POST | Create new resource | No | No |
| PUT | Replace entire resource | No | Yes |
| PATCH | Partial update | No | Yes |
| DELETE | Remove resource | No | Yes |

### Safe

"Safe" means it doesn't change anything. GET just reads - calling it 100 times has no side effects.

### Idempotent

"Idempotent" means calling it multiple times has the same effect as calling it once.

- `DELETE /tasks/5` - Call it 10 times, task 5 is still just deleted once
- `POST /tasks` - Call it 10 times, you create 10 tasks (not idempotent)

This matters for reliability. If a network fails mid-request, can you safely retry?

---

## Anatomy of an HTTP Request

```
POST /tasks HTTP/1.1                    ← Method, Path, Protocol
Host: api.myapp.com                     ← Headers start
Content-Type: application/json
Authorization: Bearer abc123xyz
                                        ← Blank line separates headers from body
{                                       ← Body (for POST/PUT/PATCH)
  "title": "Learn REST",
  "completed": false
}
```

### Parts Explained

#### 1. Method + Path

```
POST /tasks
```

What action on what resource.

#### 2. Headers

Metadata about the request:

```
Content-Type: application/json      ← "I'm sending JSON"
Authorization: Bearer abc123xyz     ← "Here's my credentials"
Accept: application/json            ← "Please send JSON back"
```

#### 3. Body

The actual data (only for POST, PUT, PATCH):

```json
{
  "title": "Learn REST",
  "completed": false
}
```

---

## Anatomy of an HTTP Response

```
HTTP/1.1 201 Created                    ← Protocol, Status Code, Status Text
Content-Type: application/json          ← Headers
Location: /tasks/42

{                                       ← Body
  "id": 42,
  "title": "Learn REST",
  "completed": false,
  "created_at": "2026-01-19T10:30:00Z"
}
```

---

## Status Codes

These tell the client what happened:

### 2xx: Success

| Code | Meaning | When to use |
|------|---------|-------------|
| 200 | OK | General success, returning data |
| 201 | Created | New resource created (POST) |
| 204 | No Content | Success, nothing to return (DELETE) |

### 4xx: Client Error (client did something wrong)

| Code | Meaning | When to use |
|------|---------|-------------|
| 400 | Bad Request | Invalid data sent |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Logged in but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Data failed validation |

### 5xx: Server Error (server broke)

| Code | Meaning | When to use |
|------|---------|-------------|
| 500 | Internal Server Error | Bug in your code |
| 503 | Service Unavailable | Server overloaded/down |

---

## Path Parameters vs Query Parameters

Two ways to pass information in the URL:

### Path Parameters

Part of the URL structure. Used to identify a specific resource:

```
GET /users/42/tasks/15
        ↑       ↑
      user_id  task_id
```

In code:

```python
@app.get("/users/{user_id}/tasks/{task_id}")
def get_task(user_id: int, task_id: int):
    # user_id = 42, task_id = 15
```

### Query Parameters

After the `?`. Used for filtering, sorting, pagination:

```
GET /tasks?completed=true&sort=created_at&limit=10
           └─────────── query string ───────────┘
```

In code:

```python
@app.get("/tasks")
def list_tasks(completed: bool = None, sort: str = None, limit: int = 10):
    # filter and return tasks
```

### When to Use Which

| Use Path Parameters | Use Query Parameters |
|---------------------|----------------------|
| Identifying a specific resource | Filtering a collection |
| Required for the route to make sense | Optional modifiers |
| `/users/42` | `/users?active=true` |
| `/tasks/15` | `/tasks?sort=date&limit=20` |

---

## A Complete Example: Task API

Let's design a full API for tasks:

### Resource: Task

```json
{
  "id": 1,
  "title": "Learn REST APIs",
  "description": "Understand endpoints and routes",
  "completed": false,
  "created_at": "2026-01-19T10:00:00Z",
  "updated_at": "2026-01-19T10:00:00Z"
}
```

### Endpoints

| Endpoint | Purpose | Request Body | Response |
|----------|---------|--------------|----------|
| `GET /tasks` | List all tasks | None | Array of tasks |
| `GET /tasks/{id}` | Get one task | None | Single task |
| `POST /tasks` | Create task | Task data (no id) | Created task (with id) |
| `PUT /tasks/{id}` | Replace task | Full task data | Updated task |
| `PATCH /tasks/{id}` | Partial update | Only fields to change | Updated task |
| `DELETE /tasks/{id}` | Delete task | None | 204 No Content |

### Example Requests and Responses

#### Create a task

Request:
```http
POST /tasks
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

Response:
```http
HTTP/1.1 201 Created
Location: /tasks/42

{
  "id": 42,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-19T14:30:00Z",
  "updated_at": "2026-01-19T14:30:00Z"
}
```

#### List tasks with filter

Request:
```http
GET /tasks?completed=false&limit=5
```

Response:
```http
HTTP/1.1 200 OK

[
  {"id": 42, "title": "Buy groceries", "completed": false, ...},
  {"id": 43, "title": "Call mom", "completed": false, ...}
]
```

#### Update just completion status

Request:
```http
PATCH /tasks/42
Content-Type: application/json

{
  "completed": true
}
```

Response:
```http
HTTP/1.1 200 OK

{
  "id": 42,
  "title": "Buy groceries",
  "completed": true,
  "updated_at": "2026-01-19T15:00:00Z",
  ...
}
```

#### Delete a task

Request:
```http
DELETE /tasks/42
```

Response:
```http
HTTP/1.1 204 No Content
```

---

## Common REST Design Patterns

### Nested Resources

When resources belong to other resources:

```
GET  /users/5/tasks      ← All tasks for user 5
POST /users/5/tasks      ← Create task for user 5
GET  /users/5/tasks/10   ← Get specific task for user 5
```

### Filtering, Sorting, Pagination

```
GET /tasks?status=pending              ← Filter
GET /tasks?sort=-created_at            ← Sort (- = descending)
GET /tasks?page=2&per_page=20          ← Pagination
GET /tasks?status=pending&sort=title&page=1&per_page=10  ← Combined
```

### Bulk Operations

```
POST /tasks/bulk        ← Create many at once
DELETE /tasks/bulk      ← Delete many (with IDs in body)
```

---

## What's NOT REST

Some things people confuse with REST:

| Not REST | Why |
|----------|-----|
| Using verbs in URLs | `/getUsers`, `/createTask` - use HTTP methods instead |
| Using only POST | Some APIs use POST for everything - this ignores HTTP semantics |
| GraphQL | Different paradigm (single endpoint, query language) |
| RPC | Remote Procedure Call - calling functions, not accessing resources |

### Bad vs Good URL Design

| Bad (Not RESTful) | Good (RESTful) |
|-------------------|----------------|
| `GET /getUsers` | `GET /users` |
| `POST /createTask` | `POST /tasks` |
| `POST /deleteUser?id=5` | `DELETE /users/5` |
| `GET /getUserTasks?userId=5` | `GET /users/5/tasks` |

---

## Quick Reference

### Concepts

| Concept | Definition |
|---------|------------|
| Resource | A "thing" in your system (user, task, order) |
| URL | Address of a resource |
| Endpoint | URL + HTTP method |
| Route | Code that handles an endpoint |
| HTTP Method | The verb (GET, POST, PUT, DELETE) |
| Status Code | Number indicating result (200, 404, 500) |
| Headers | Metadata about request/response |
| Body | The actual data payload |
| Path Parameter | Variable in URL path (`/users/{id}`) |
| Query Parameter | Filter/options after `?` (`?sort=name`) |

### HTTP Methods Quick Reference

| Method | CRUD Operation | Typical Response Code |
|--------|---------------|----------------------|
| GET | Read | 200 OK |
| POST | Create | 201 Created |
| PUT | Update (full) | 200 OK |
| PATCH | Update (partial) | 200 OK |
| DELETE | Delete | 204 No Content |

### Common Headers

| Header | Purpose | Example |
|--------|---------|---------|
| Content-Type | Format of request body | `application/json` |
| Accept | Desired response format | `application/json` |
| Authorization | Authentication credentials | `Bearer <token>` |
| Location | URL of created resource | `/tasks/42` |

---

## Next Steps

Now that you understand REST:

1. **Design your API** - Plan your resources and endpoints before coding
2. **Build the backend** - Implement routes with FastAPI
3. **Test with tools** - Use curl, Postman, or browser dev tools
4. **Build the frontend** - Create UI that calls your API
5. **Deploy** - Put it on the internet

---

*Document created: January 2026*
*For learning web development and deployment*
