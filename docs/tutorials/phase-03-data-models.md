# Phase 3: Data Models with Pydantic - Complete Tutorial

## Learning Objectives

By the end of this phase, you will understand:
- What data validation is and why it matters
- How Pydantic models work under the hood
- Type hints in Python and their benefits
- How to define request and response schemas
- The concept of API contracts
- How FastAPI uses Pydantic for automatic validation

---

## 1. The Data Validation Problem

### Why Validate Data?

Your API receives data from the outside world. That data could be:
- Malformed (missing fields, wrong types)
- Malicious (SQL injection, XSS attacks)
- Accidental mistakes (typos, wrong format)

Without validation, bad data causes crashes, security vulnerabilities, or corrupted state.

### The Naive Approach

```python
@app.post("/unfurl")
def unfurl(data):
    url = data["url"]  # What if "url" doesn't exist? KeyError!
    response = fetch(url)  # What if url is not a string? TypeError!
    return {"result": response}
```

Problems:
- Crashes if "url" key is missing
- Crashes if "url" is not a valid URL
- No clear error message for the user
- Security vulnerabilities

### The Manual Validation Approach

```python
@app.post("/unfurl")
def unfurl(data):
    # Check if data is a dict
    if not isinstance(data, dict):
        return {"error": "Request body must be JSON object"}, 400

    # Check if url exists
    if "url" not in data:
        return {"error": "Missing required field: url"}, 400

    url = data["url"]

    # Check if url is a string
    if not isinstance(url, str):
        return {"error": "url must be a string"}, 400

    # Check if url is not empty
    if not url.strip():
        return {"error": "url cannot be empty"}, 400

    # Check if url starts with http
    if not url.startswith(("http://", "https://")):
        return {"error": "url must start with http:// or https://"}, 400

    # Check url length
    if len(url) > 2048:
        return {"error": "url too long (max 2048 characters)"}, 400

    # Actually do the work...
    response = fetch(url)
    return {"result": response}
```

Problems:
- 30+ lines just for ONE field
- Easy to forget edge cases
- Repetitive across endpoints
- Error messages inconsistent
- Hard to maintain

### The Pydantic Approach

```python
from pydantic import BaseModel, HttpUrl

class UnfurlRequest(BaseModel):
    url: HttpUrl

@app.post("/unfurl")
def unfurl(request: UnfurlRequest):
    # If we reach here, request.url is GUARANTEED to be a valid HTTP URL
    response = fetch(str(request.url))
    return {"result": response}
```

**3 lines of model definition replace 30+ lines of manual validation!**

Pydantic automatically:
- Checks the field exists
- Checks it is a string
- Checks it is a valid URL format
- Returns helpful error messages
- Documents the expected input

---

## 2. Understanding Type Hints

### What Are Type Hints?

Type hints tell Python (and developers) what type a variable should be:

```python
# Without type hints
def greet(name):
    return f"Hello, {name}"

# With type hints
def greet(name: str) -> str:
    return f"Hello, {name}"
```

The `: str` says "name should be a string"
The `-> str` says "this function returns a string"

### Type Hints Don't Enforce Anything (By Default)

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

greet(123)  # Python runs this! No error!
```

Type hints are just **annotations**. Python ignores them at runtime. They are for:
- Documentation (developers know what to pass)
- IDE support (autocomplete, error highlighting)
- Static type checkers (mypy, pyright)
- **Pydantic** (which DOES enforce them!)

### Common Type Hints

```python
# Basic types
name: str = "Alice"
age: int = 30
price: float = 19.99
active: bool = True

# Collections
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 100, "Bob": 95}
coordinates: tuple[float, float] = (1.5, 2.5)

# Optional (can be None)
from typing import Optional
nickname: Optional[str] = None  # Can be str or None

# Union (multiple possible types)
from typing import Union
id: Union[int, str] = 123  # Can be int or str

# Modern Python 3.10+ syntax
id: int | str = 123  # Same as Union[int, str]
nickname: str | None = None  # Same as Optional[str]
```

### Special Pydantic Types

Pydantic provides validated types:

```python
from pydantic import (
    HttpUrl,      # Must be valid HTTP/HTTPS URL
    EmailStr,     # Must be valid email
    PositiveInt,  # Must be positive integer
    SecretStr,    # Hidden in logs/repr
    FilePath,     # Must be existing file path
)

class User(BaseModel):
    email: EmailStr           # "alice@example.com" ✓, "not-email" ✗
    website: HttpUrl          # "https://x.com" ✓, "ftp://x" ✗
    age: PositiveInt          # 25 ✓, -5 ✗, 0 ✗
    password: SecretStr       # Shown as "**********" in logs
```

---

## 3. Pydantic BaseModel Deep Dive

### Creating a Model

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str
```

This creates a class that:
- Has `name`, `age`, `email` attributes
- Validates data on creation
- Can serialize to JSON
- Has helpful string representation

### Creating Instances

```python
# From keyword arguments
user = User(name="Alice", age=30, email="alice@example.com")

# From dictionary
data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
user = User(**data)  # ** unpacks the dict

# From JSON string
import json
json_str = '{"name": "Alice", "age": 30, "email": "alice@example.com"}'
user = User.model_validate_json(json_str)
```

### Automatic Type Coercion

Pydantic tries to convert values to the correct type:

```python
class User(BaseModel):
    age: int

# String "30" becomes int 30
user = User(age="30")
print(user.age)  # 30 (int, not str!)
print(type(user.age))  # <class 'int'>

# But invalid strings fail
user = User(age="thirty")  # ValidationError!
```

This is **coercion** - Pydantic converts when possible.

### Validation Errors

When validation fails, Pydantic raises `ValidationError`:

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    name: str
    age: int

try:
    user = User(name="Alice", age="not-a-number")
except ValidationError as e:
    print(e)
```

Output:
```
1 validation error for User
age
  Input should be a valid integer, unable to parse string as an integer
  [type=int_parsing, input_value='not-a-number', input_type=str]
```

The error tells you:
- Which field failed (`age`)
- What went wrong (`unable to parse string as an integer`)
- What was provided (`'not-a-number'`)

### Default Values

```python
class User(BaseModel):
    name: str                    # Required
    age: int = 0                 # Optional, defaults to 0
    active: bool = True          # Optional, defaults to True

user = User(name="Alice")
print(user.age)     # 0
print(user.active)  # True
```

### Optional Fields

```python
from typing import Optional

class User(BaseModel):
    name: str
    nickname: Optional[str] = None  # Can be str or None, defaults to None

user = User(name="Alice")
print(user.nickname)  # None

user = User(name="Alice", nickname="Ali")
print(user.nickname)  # "Ali"
```

**Important distinction:**
- `age: int = 0` - Field is optional, defaults to 0, must be int
- `nickname: Optional[str] = None` - Field is optional, defaults to None, can be str or None

### Serialization

Convert models to different formats:

```python
class User(BaseModel):
    name: str
    age: int

user = User(name="Alice", age=30)

# To dictionary
user.model_dump()
# {'name': 'Alice', 'age': 30}

# To JSON string
user.model_dump_json()
# '{"name":"Alice","age":30}'

# Exclude fields
user.model_dump(exclude={"age"})
# {'name': 'Alice'}

# Include only certain fields
user.model_dump(include={"name"})
# {'name': 'Alice'}
```

---

## 4. Our Models Explained

Now let us understand the models we created for our link previewer:

### UnfurlRequest - The Input Model

```python
from pydantic import BaseModel, HttpUrl

class UnfurlRequest(BaseModel):
    url: HttpUrl
```

**What this does:**

1. **Accepts JSON like:** `{"url": "https://example.com"}`

2. **HttpUrl validation checks:**
   - String is not empty
   - Starts with http:// or https://
   - Has valid URL structure (scheme, host, path)
   - URL-encodes special characters

3. **Rejects:**
   - `{"url": "not-a-url"}` - Invalid URL format
   - `{"url": "ftp://example.com"}` - Not HTTP/HTTPS
   - `{"url": ""}` - Empty string
   - `{}` - Missing url field
   - `{"URL": "..."}` - Wrong case (url vs URL)

### UnfurlData - The Extracted Metadata

```python
class UnfurlData(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    site_name: Optional[str] = None
```

**Why all fields are Optional:**

Not every webpage has all metadata:
- A minimal HTML page might only have a `<title>`
- Some pages have no Open Graph tags
- Images are often missing

We use `Optional[str] = None` so we can return partial data:

```python
# Page with everything
UnfurlData(
    url="https://example.com",
    title="Example",
    description="A page",
    image="https://example.com/img.png",
    site_name="Example Site"
)

# Page with just title
UnfurlData(
    url="https://example.com",
    title="Example"
    # description, image, site_name all default to None
)
```

**Why url is str, not HttpUrl:**

We echo back the original URL as a plain string. It was already validated in UnfurlRequest, so we do not need to re-validate.

### UnfurlResponse - The API Response

```python
class UnfurlResponse(BaseModel):
    success: bool
    data: Optional[UnfurlData] = None
    error: Optional[str] = None
```

**Why this structure:**

This is a common API response pattern:

```python
# Success case
UnfurlResponse(
    success=True,
    data=UnfurlData(url="...", title="..."),
    error=None
)

# Error case
UnfurlResponse(
    success=False,
    data=None,
    error="Could not fetch URL: timeout"
)
```

Benefits:
- Client always knows if request succeeded (check `success`)
- Success response has `data`
- Error response has `error` message
- Consistent structure for all responses

### Nested Models

Notice that `UnfurlResponse` contains `UnfurlData`:

```python
class UnfurlResponse(BaseModel):
    success: bool
    data: Optional[UnfurlData] = None  # Another Pydantic model!
```

Pydantic handles nested models automatically:

```python
response = UnfurlResponse(
    success=True,
    data={  # Can pass dict, Pydantic converts to UnfurlData
        "url": "https://example.com",
        "title": "Example"
    }
)

print(response.data.title)  # "Example"
print(type(response.data))  # <class 'UnfurlData'>
```

---

## 5. API Contracts

### What is an API Contract?

An **API contract** is a formal definition of:
- What the API accepts (request format)
- What the API returns (response format)
- What errors might occur

It is like a legal contract between your API and its users.

### Why Contracts Matter

**Without a contract:**
- Users guess what to send
- You change the API, users' code breaks
- No documentation
- Endless support questions

**With a contract:**
- Users know exactly what to send
- Changes are intentional and communicated
- Auto-generated documentation
- Self-service for users

### Our API Contract

**Endpoint:** `POST /unfurl`

**Request:**
```json
{
  "url": "https://example.com"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| url | HttpUrl | Yes | The URL to extract metadata from |

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "This domain is for illustrative examples.",
    "image": "https://example.com/image.png",
    "site_name": "Example"
  },
  "error": null
}
```

**Error Response (200):**
```json
{
  "success": false,
  "data": null,
  "error": "Could not fetch URL: Connection timeout"
}
```

**Validation Error (422):**
```json
{
  "detail": [
    {
      "type": "url_parsing",
      "loc": ["body", "url"],
      "msg": "Input should be a valid URL",
      "input": "not-a-url"
    }
  ]
}
```

### FastAPI Auto-Documentation

Because we use Pydantic models, FastAPI automatically generates:

1. **OpenAPI Schema** (`/openapi.json`) - Machine-readable API spec
2. **Swagger UI** (`/docs`) - Interactive documentation
3. **ReDoc** (`/redoc`) - Alternative documentation

You get free, always-up-to-date documentation!

---

## 6. How FastAPI Uses Pydantic

### Request Body Validation

```python
@app.post("/unfurl")
def unfurl(request: UnfurlRequest):
    # FastAPI automatically:
    # 1. Reads JSON from request body
    # 2. Validates it against UnfurlRequest
    # 3. Returns 422 if validation fails
    # 4. Passes validated UnfurlRequest to your function
    pass
```

The magic is in the type hint: `request: UnfurlRequest`

FastAPI sees a Pydantic model and knows to:
1. Parse the request body as JSON
2. Validate against the model
3. Return errors if invalid

### Response Model Validation

```python
@app.post("/unfurl", response_model=UnfurlResponse)
def unfurl(request: UnfurlRequest) -> UnfurlResponse:
    # FastAPI also validates the RESPONSE
    # If you return wrong data, it errors
    return UnfurlResponse(success=True, data=...)
```

`response_model=UnfurlResponse` ensures:
- Response matches the schema
- Extra fields are stripped
- Documentation shows response format

### The Complete Flow

```
1. Client sends:     POST /unfurl {"url": "https://example.com"}
                            │
                            ▼
2. FastAPI parses:   JSON body → Python dict
                            │
                            ▼
3. Pydantic validates: dict → UnfurlRequest (or 422 error)
                            │
                            ▼
4. Your code runs:   def unfurl(request: UnfurlRequest)
                            │
                            ▼
5. You return:       UnfurlResponse(success=True, data=...)
                            │
                            ▼
6. Pydantic serializes: UnfurlResponse → JSON
                            │
                            ▼
7. Client receives:  {"success": true, "data": {...}}
```

---

## 7. Advanced Pydantic Features

### Field Validators

Add custom validation logic:

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age: int

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()  # Also strips whitespace

    @field_validator('age')
    @classmethod
    def age_must_be_reasonable(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```

### Field Constraints

Use `Field()` for additional constraints:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)  # ge=greater or equal, le=less or equal
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

### Model Configuration

Customize model behavior:

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Strip whitespace from strings
        str_min_length=1,           # All strings must have at least 1 char
        extra='forbid',             # Error if extra fields provided
    )

    name: str
    age: int

# Extra fields cause error
User(name="Alice", age=30, unknown="field")  # ValidationError!
```

### Computed Fields

Fields calculated from other fields:

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

rect = Rectangle(width=10, height=5)
print(rect.area)  # 50.0
```

---

## 8. Testing Our Models

Let us verify our models work correctly:

```python
from app.models import UnfurlRequest, UnfurlData, UnfurlResponse
from pydantic import ValidationError

# Test 1: Valid URL
req = UnfurlRequest(url="https://example.com")
print(f"Valid URL: {req.url}")  # https://example.com/

# Test 2: Invalid URL
try:
    req = UnfurlRequest(url="not-a-url")
except ValidationError as e:
    print(f"Invalid URL error: {e.errors()[0]['msg']}")

# Test 3: Missing URL
try:
    req = UnfurlRequest()
except ValidationError as e:
    print(f"Missing URL error: {e.errors()[0]['msg']}")

# Test 4: Full response
data = UnfurlData(
    url="https://example.com",
    title="Example",
    description="A test page"
)
response = UnfurlResponse(success=True, data=data)
print(f"Response JSON: {response.model_dump_json()}")

# Test 5: Error response
error_response = UnfurlResponse(success=False, error="Connection timeout")
print(f"Error JSON: {error_response.model_dump_json()}")
```

Expected output:
```
Valid URL: https://example.com/
Invalid URL error: Input should be a valid URL, relative URL without a base
Missing URL error: Field required
Response JSON: {"success":true,"data":{"url":"https://example.com","title":"Example","description":"A test page","image":null,"site_name":null},"error":null}
Error JSON: {"success":false,"data":null,"error":"Connection timeout"}
```

---

## 9. Commands Reference

### Pydantic Model Operations

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# Create from kwargs
user = User(name="Alice", age=30)

# Create from dict
user = User(**{"name": "Alice", "age": 30})

# Create from JSON string
user = User.model_validate_json('{"name": "Alice", "age": 30}')

# Convert to dict
user.model_dump()

# Convert to JSON string
user.model_dump_json()

# Get JSON schema
User.model_json_schema()

# Check if valid (without raising)
User.model_validate({"name": "Alice", "age": 30})  # Returns User or raises
```

### Type Checking with mypy

```bash
# Install mypy
pip install mypy

# Check types
mypy app/models.py

# Check entire project
mypy app/
```

---

## 10. Self-Check Questions

1. **What happens if you send `{"URL": "https://example.com"}` (capital URL)?**

   Answer: Validation fails because the field name is case-sensitive. The model expects `url` (lowercase). You get a "Field required" error for `url`.

2. **Why use `Optional[str] = None` instead of just `str = None`?**

   Answer: `Optional[str]` explicitly states the field can be `str` OR `None`. Just `str = None` is ambiguous - the default is None but the type says str. `Optional[str] = None` is self-documenting.

3. **What is the difference between Pydantic validation and Python type hints?**

   Answer: Python type hints are just annotations - Python ignores them at runtime. Pydantic actually enforces them, raising ValidationError if types don't match.

4. **Why do we have both UnfurlData and UnfurlResponse?**

   Answer: Separation of concerns. UnfurlData is the actual metadata extracted. UnfurlResponse is the API wrapper that includes success/error status. This lets us reuse UnfurlData in different contexts.

5. **What does HttpUrl validate that str does not?**

   Answer: HttpUrl checks that the string is a valid URL with http:// or https:// scheme, valid host, proper structure. str accepts any string.

6. **How does FastAPI know to validate the request body?**

   Answer: The type hint `request: UnfurlRequest` tells FastAPI to parse the JSON body and validate it against UnfurlRequest. FastAPI inspects function signatures for Pydantic models.

7. **What HTTP status code does FastAPI return for validation errors?**

   Answer: 422 Unprocessable Entity. This indicates the request was syntactically correct (valid JSON) but semantically invalid (failed validation).

8. **Can Pydantic convert `"30"` to `int`?**

   Answer: Yes! Pydantic performs type coercion. String `"30"` becomes integer `30`. But `"thirty"` would fail because it cannot be parsed as an integer.

---

## Next Phase

Now that you understand data models and validation, we will implement the URL extraction logic that actually fetches pages and parses metadata in **Phase 4: URL Extraction Logic**.
