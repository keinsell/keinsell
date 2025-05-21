# 🐫 Kamel

**🐫 Kamel** is semi-experimental repository setup for full-stack OCaml-based applications. It includes a Dream-based RESTful API server written in Reason.

## Functional Requirements

### 1. Identity Management

#### 1.1 Authentication

- Users must be able to obtain a valid session or JWT by supplying valid credentials.
  - Endpoint: `POST /api/auth/login`
  - Request body:
    ```json
    { "email": "<string>", "password": "<string>" }
    ```
  - Success response: HTTP 200 + `{ "token": "<jwt>", "expiresIn": <integer> }`
  - Failure response: HTTP 401 + `{ "error": "Invalid email or password" }`
- All protected endpoints must reject requests without a valid token or session cookie.

#### 1.2 Authorization

- Define two user roles:
  - `user` – can manage own appointments.
  - `admin` – can manage all users and appointments.
- Access control:
  - `GET /api/appointments`
    - `user` → returns only their own appointments
    - `admin` → returns all appointments
  - `DELETE /api/users/:id`
    - only `admin` may delete arbitrary users
- Unauthorized access must return HTTP 403 + `{ "error": "Forbidden" }`.

### 2. User Management

#### 2.1 Registration

- New users register by providing name, email, and password.
  - Endpoint: `POST /api/users`
  - Request body:
    ```json
    {
      "name": "<string>",
      "email": "<valid email>",
      "password": "<min-8-char string>"
    }
    ```
  - Validation:
    - `email` must be unique
    - `password` must be ≥ 8 characters
  - Success: HTTP 201 + `{ "id": "<uuid>", "name": "...", "email": "..." }`
  - Errors:
    - HTTP 400 + `{ "error": "Email already in use" }`
    - HTTP 422 + `{ "error": "Password too short" }`

#### 2.2 Login

- Existing users log in to receive a session or JWT.
  - See **Authentication** above.

### 3. Booking (Appointment) Management

#### 3.1 Create Appointment

- Authenticated users can book an appointment.
  - Endpoint: `POST /api/appointments`
  - Request body:
    ```json
    {
      "date": "<ISO8601 datetime>",
      "service": "<string>",
      "notes"?: "<string>"
    }
    ```
  - Validation:
    - `date` must be in the future
    - `service` must be one of the pre-configured service types
  - Success: HTTP 201 + full appointment record
  - Failure: HTTP 400 + field-specific error messages

#### 3.2 List Appointments

- Users can list their own appointments; admins can list all.
  - Endpoint: `GET /api/appointments`
  - Query parameters (optional):
    - `from=<ISO8601 date>`
    - `to=<ISO8601 date>`
    - `status=pending|confirmed|cancelled`
  - Response: HTTP 200 + `[{ "id": "...", "userId": "...", "date": "...", "service": "...", "status": "..." }, …]`

#### 3.3 Update Appointment

- Users can modify only their own appointments before a configurable cutoff (e.g. 24 hours prior).
  - Endpoint: `PUT /api/appointments/:id`
  - Request body: same as create, with optional updates
  - Constraints:
    - Cannot change past appointments
    - Must respect cutoff window
  - Success: HTTP 200 + updated appointment
  - Unauthorized or invalid modification: HTTP 403 or 400

#### 3.4 Cancel Appointment

- Users may cancel their own future appointments.
  - Endpoint: `PATCH /api/appointments/:id/cancel`
  - Success: HTTP 200 + `{ "status": "cancelled" }`
  - Failure: HTTP 404 if not found; HTTP 403 if not allowed

#### 3.5 Admin Controls

- Admins can confirm, reschedule, or cancel any appointment.
  - Example: `PATCH /api/appointments/:id/status` with `{ "status": "confirmed" }`

## Quick Start

### Running the API Server

1. Clone the repository
2. Enter the development shell:

```bash
nix develop
```

3. Build and run the project:

```bash
dune exec kamel
```

The API server will start on port 8080. You can access the following endpoints:

- `GET http://localhost:8080/api/health` - Health check
- `GET http://localhost:8080/api/todos` - List all todos
- `GET http://localhost:8080/api/todos/stats` - Get todo statistics
- `POST http://localhost:8080/api/todos` - Create a new todo
- `GET http://localhost:8080/api/todos/:id` - Get a specific todo
- And more! See the [API Documentation](API_DOCS.md) for details.

### Testing the API

You can use the included test script to quickly test all API endpoints:

```bash
./bin/test_api.sh
```

## Development

This project uses the Flakelight framework to simplify Nix flake setup and provide a consistent development environment.

### Prerequisites

- [Nix](https://nixos.org/download.html) package manager with flakes enabled

### Getting Started

1. Clone the repository
2. Enter the development shell:

```bash
nix develop
```

3. Build the project:

```bash
dune build
```

4. Run tests:

```bash
dune test
```

## Nix Flake

This project uses [Flakelight](https://github.com/nix-community/flakelight), a framework for simplifying Nix flake setup. The flake configuration provides:

- A development environment with OCaml, OPAM, Dune, UTop, and other development tools
- A buildable package definition for the project
- Proper integration with OCaml tools like LSP, Reason, and Melange

### Flake Structure

The flake.nix file is structured as follows:

- **inputs**: Dependencies for the flake (nixpkgs, flakelight, opam-nix)
- **package**: Definition for building the OCaml package
- **devShell**: Configuration for the development environment

## Project Structure

- `lib/`: OCaml source code for libraries
- `bin/`: OCaml source code for executables
- `test/`: Test files
- `_build/`: Build artifacts (generated by Dune)

## References

- [_Backend WebDev w/ Dream and Caqti_](https://ceramichacker.com/blog/28-2x-backend-webdev-w-dream-and-caqti)
