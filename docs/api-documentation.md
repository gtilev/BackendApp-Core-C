# Accounting Data Processing API Documentation

## Overview

This API processes accounting operations from different Excel file formats and stores them in a PostgreSQL database. It supports various template formats (Ривал, АЖУР, Микроинвест, Бизнес навигатор, Универсум) and provides endpoints for file management, data retrieval, and analytics.

## Authentication

The API uses JWT (JSON Web Token) authentication. All endpoints (except login and register) require a valid token.

### Get Authentication Token

```
POST /api/auth/login
```

**Request Body:**
```json
{
  "username": "yourusername",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Register New User

```
POST /api/auth/register
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword"
}
```

## Excel File Processing

### Upload Excel File

```
POST /api/files/upload
```

**Required Headers:**
- Authorization: Bearer {token}

**Request Body:**
- Form data with 'file' field containing the Excel file (.xls or .xlsx)

**Response:**
```json
{
  "id": 1,
  "filename": "accounting_data.xlsx",
  "template_type": "rival",
  "upload_date": "2023-08-15T14:30:00",
  "processed": false,
  "file_path": "uploads/accounting_data.xlsx",
  "user_id": 1
}
```

### Process Excel File

```
POST /api/files/{file_id}/process
```

Extracts accounting operations from a previously uploaded file.

**Required Headers:**
- Authorization: Bearer {token}

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "file_id": 1,
      "operation_date": "2023-01-15",
      "document_type": "Invoice",
      "document_number": "INV-001",
      "debit_account": "411",
      "credit_account": "701",
      "amount": 1500.00,
      "description": "Service payment",
      "template_type": "rival",
      "created_at": "2023-08-15T14:35:00"
    },
    // ...more operations
  ],
  "total": 25
}
```

### List Uploaded Files

```
GET /api/files/
```

Lists all files uploaded by the authenticated user with pagination and filtering options.

**Required Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- skip (integer, optional): Number of records to skip for pagination. Default: 0
- limit (integer, optional): Maximum number of records to return. Default: 100
- template_type (string, optional): Filter by template type
- processed (boolean, optional): Filter by processing status

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "filename": "accounting_data.xlsx",
      "template_type": "rival",
      "upload_date": "2023-08-15T14:30:00",
      "processed": true,
      "file_path": "uploads/accounting_data.xlsx",
      "user_id": 1
    },
    // ...more files
  ],
  "total": 5
}
```

### Get File Details

```
GET /api/files/{file_id}
```

Gets detailed information about a specific file including operation count.

**Required Headers:**
- Authorization: Bearer {token}

**Response:**
```json
{
  "id": 1,
  "filename": "accounting_data.xlsx",
  "template_type": "rival",
  "upload_date": "2023-08-15T14:30:00",
  "processed": true,
  "file_path": "uploads/accounting_data.xlsx",
  "user_id": 1,
  "operation_count": 25
}
```

### Delete File

```
DELETE /api/files/{file_id}
```

Deletes a file and all its associated operations.

**Required Headers:**
- Authorization: Bearer {token}

**Response:**
- Status: 204 No Content

## Accounting Operations

### List Operations

```
GET /api/operations/
```

Lists accounting operations with extensive filtering options.

**Required Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- skip (integer, optional): Number of records to skip for pagination. Default: 0
- limit (integer, optional): Maximum number of records to return. Default: 100
- start_date (date, optional): Filter by operation date (from)
- end_date (date, optional): Filter by operation date (to)
- document_type (string, optional): Filter by document type
- debit_account (string, optional): Filter by debit account
- credit_account (string, optional): Filter by credit account
- min_amount (number, optional): Filter by minimum amount
- max_amount (number, optional): Filter by maximum amount
- description_contains (string, optional): Filter by description text
- template_type (string, optional): Filter by template type
- file_id (integer, optional): Filter by file ID

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "file_id": 1,
      "operation_date": "2023-01-15",
      "document_type": "Invoice",
      "document_number": "INV-001",
      "debit_account": "411",
      "credit_account": "701",
      "amount": 1500.00,
      "description": "Service payment",
      "template_type": "rival",
      "created_at": "2023-08-15T14:35:00"
    },
    // ...more operations
  ],
  "total": 150
}
```

### Get Operation Details

```
GET /api/operations/{operation_id}
```

Gets detailed information about a specific accounting operation.

**Required Headers:**
- Authorization: Bearer {token}

**Response:**
```json
{
  "id": 1,
  "file_id": 1,
  "operation_date": "2023-01-15",
  "document_type": "Invoice",
  "document_number": "INV-001",
  "debit_account": "411",
  "credit_account": "701",
  "amount": 1500.00,
  "description": "Service payment",
  "partner_name": "Client XYZ",
  "analytical_debit": null,
  "analytical_credit": null,
  "template_type": "rival",
  "created_at": "2023-08-15T14:35:00",
  "raw_data": {
    // Original Excel data
  }
}
```

### Get Operations Summary

```
GET /api/operations/statistics/summary
```

Gets summary statistics about accounting operations.

**Required Headers:**
- Authorization: Bearer {token}

**Query Parameters:**
- start_date (date, optional): Filter by operation date (from)
- end_date (date, optional): Filter by operation date (to)

**Response:**
```json
{
  "total_operations": 150,
  "total_amount": 250000.50,
  "template_counts": {
    "rival": 45,
    "ajur": 55,
    "microinvest": 20,
    "business_navigator": 15,
    "universum": 15
  }
}
```

## Using the API with Swagger UI

FastAPI automatically generates interactive API documentation using Swagger UI. You can access it at:

```
http://your-api-url/docs
```

The Swagger UI provides a user-friendly interface to:

1. View all available endpoints
2. Read detailed parameter specifications
3. Try out API calls directly from the browser
4. See request and response examples

## Supported Excel Templates

The API supports the following Excel template formats:

1. **Ривал**: 
   - Column layout: вид документ, номер на документ, дата, име, дебит, кредит, сума, обяснение

2. **АЖУР**:
   - Column layout: вид, номер, дата, дебит, аналитична, кредит, аналитична, сума, обяснение

3. **Микроинвест**:
   - Column layout: дебит с-ка, кедит с-ка, вид документ, дата, номер на док, партньор, основание

4. **Бизнес навигатор**:
   - Column layout: док тип, док номер, док дата, счетоводен текст, сума дебит, номер на сметка, име на сметка, сметката която се кредитира

5. **Универсум**:
   - Specific columns: C, E, F, I, J, K, L, P