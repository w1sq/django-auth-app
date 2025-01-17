# Django Authentication API

This project is a Django-based authentication API that provides user registration, login, token management, and user information retrieval. It utilizes Django REST Framework for building the API and includes JWT (JSON Web Tokens) for secure authentication.

## Features

-   User registration with email and password
-   User login to obtain access and refresh tokens
-   Token refresh functionality
-   User logout to invalidate refresh tokens
-   Retrieve and update user information
-   API documentation using Swagger and ReDoc

## Requirements

-   Docker

## Installation

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/w1sq/django-auth-app.git
cd django-auth-app
```

### Step 2: Build the Docker Image

Run the following command to build the Docker image:

```bash
docker build -t django-auth-app .
```

### Step 3: Run the Docker Container

After the image is built, you can run a container from that image with the following command:

```bash
docker run -d -p 8000:8000 django-auth-app
```

**Note**: If you encounter a port conflict (e.g., "port is already allocated"), you can either stop the process using port 8000 or run the container on a different port:

```bash
docker run -d -p 8001:8000 django-auth-app
```

In this case, you would access your application at `http://localhost:8001`.

### Step 5: Access Your Application

Once the container is running, you can access your Django application by navigating to `http://localhost:8000` (or `http://localhost:8001` if you changed the port) in your web browser.

### Step 6: Stopping the Container

If you need to stop the container, you can find the container ID or name using:

```bash
docker ps
```

Then stop it with:

```bash
docker stop <container_id_or_name>
```

## API Endpoints

### User Registration

-   **Endpoint**: `/api/register/`
-   **Method**: `POST`
-   **Body**:

    ```json
    {
        "email": "user@example.com",
        "password": "password"
    }
    ```

-   **Response**:

    ```json
    {
        "id": 1,
        "email": "user@example.com"
    }
    ```

### User Login

-   **Endpoint**: `/api/login/`
-   **Method**: `POST`
-   **Body**:

    ```json
    {
        "email": "user@example.com",
        "password": "password"
    }
    ```

-   **Response**:

    ```json
    {
        "access_token": "your_access_token",
        "refresh_token": "your_refresh_token"
    }
    ```

### Token Refresh

-   **Endpoint**: `/api/refresh/`
-   **Method**: `POST`
-   **Body**:

    ```json
    {
        "refresh_token": "your_refresh_token"
    }
    ```

-   **Response**:

    ```json
    {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token"
    }
    ```

### User Logout

-   **Endpoint**: `/api/logout/`
-   **Method**: `POST`
-   **Body**:

    ```json
    {
        "refresh_token": "your_refresh_token"
    }
    ```

-   **Response**:

    ```json
    {
        "success": "User logged out."
    }
    ```

### Retrieve User Information

-   **Endpoint**: `/api/me/`
-   **Method**: `GET`
-   **Headers**:

    ```
    Authorization: Bearer your_access_token
    ```

-   **Response**:

    ```json
    {
        "id": 1,
        "username": "user_name",
        "email": "user@example.com"
    }
    ```

### Update User Information

-   **Endpoint**: `/api/me/`
-   **Method**: `PUT`
-   **Headers**:

    ```
    Authorization: Bearer your_access_token
    ```

-   **Body**:

    ```json
    {
        "username": "new_username"
    }
    ```

-   **Response**:

    ```json
    {
        "id": 1,
        "username": "new_username",
        "email": "user@example.com"
    }
    ```

## API Documentation

The API documentation is available at:

-   Swagger UI: `/swagger/`
-   ReDoc: `/redoc/`

## Contact

For any inquiries, please contact [artem.kokorev2005@yandex.ru].
