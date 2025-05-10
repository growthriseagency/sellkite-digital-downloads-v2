# Digital Downloads API Documentation

---

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Models Overview](#models-overview)
4. [API Endpoints](#api-endpoints)
    - [Plan Management](#plan-management)
    - [Store Management & Onboarding](#store-management--onboarding)
    - [Subscription Management](#subscription-management)
    - [Product Management](#product-management)
    - [File Management](#file-management)
    - [License Key Management](#license-key-management)
    - [Order & Fulfillment (Shopify Webhooks)](#order--fulfillment-shopify-webhooks)
    - [Customer Download](#customer-download)
5. [Error Handling](#error-handling)
6. [Non-Functional Notes](#non-functional-notes)

---

## Introduction
This API enables Shopify merchants to deliver digital products to their customers. It supports:
- Digital product and license key management
- Automated fulfillment via Shopify webhooks
- Secure customer download links
- Tiered subscription plans and usage tracking

---

## Authentication
- Most merchant-facing endpoints require authentication (e.g., via session or token, depending on deployment).
- Public endpoints (e.g., customer download) do not require authentication.

---

## Models Overview

### Plan
- `id`: integer
- `name`: string
- `price_monthly`: decimal
- `price_annually`: decimal (optional)
- `max_products`: integer (nullable)
- `max_orders_per_month`: integer (nullable)
- `max_storage_gb`: integer (nullable)
- `allow_custom_email_template`: boolean
- `is_active`: boolean
- `created_at`, `updated_at`: datetime

### Store
- `id`: integer
- `shopify_domain`: string
- `shopify_access_token`: string
- `email`: string (optional)
- `is_active`: boolean
- `current_plan`: Plan (FK)
- `subscription_id_external`: string (optional)
- `subscription_status`: string (optional)
- `current_billing_period_ends`: datetime (optional)
- `current_product_count`: integer
- `current_storage_used_bytes`: integer
- `current_month_order_count`: integer
- `last_order_count_reset_at`: datetime (optional)
- `created_at`, `updated_at`: datetime

### Product
- `id`: integer
- `store`: Store (FK)
- `shopify_product_id`: integer
- `shopify_variant_id`: integer (nullable)
- `name`: string
- `is_digital`: boolean
- `max_downloads_per_link`: integer
- `link_expiration_hours`: integer
- `created_at`, `updated_at`: datetime

### File
- `id`: integer
- `product`: Product (FK)
- `file_name`: string
- `file_path`: string (S3/Spaces path)
- `file_type`: string (optional)
- `file_size_bytes`: integer
- `display_name`: string (optional)
- `upload_date`, `updated_at`: datetime

### LicenseKey
- `id`: integer
- `product`: Product (FK)
- `key`: string
- `is_assigned`: boolean
- `created_at`, `updated_at`: datetime

### Order
- `id`: integer
- `store`: Store (FK)
- `shopify_order_id`: integer
- `email`: string
- `created_at`, `updated_at`: datetime

### OrderItem
- `id`: integer
- `order`: Order (FK)
- `product`: Product (FK)
- `quantity`: integer
- `created_at`, `updated_at`: datetime

### DownloadLink
- `id`: integer
- `order_item`: OrderItem (FK)
- `uuid`: UUID
- `url`: string
- `expires_at`: datetime
- `download_count`: integer
- `created_at`, `updated_at`: datetime

### AssignedLicenseKey
- `id`: integer
- `order_item`: OrderItem (FK)
- `license_key`: LicenseKey (FK)
- `assigned_at`: datetime

---

## API Endpoints

### 1. Plan Management
#### `GET /api/v1/plans/`
- **Description:** List all available active subscription plans.
- **Response:**
```json
[
  {
    "id": 1,
    "name": "Basic",
    "price_monthly": "9.99",
    "price_annually": "99.99",
    "max_products": 10,
    "max_orders_per_month": 100,
    "max_storage_gb": 5,
    "allow_custom_email_template": false
  },
  ...
]
```

---

### 2. Store Management & Onboarding
#### `POST /api/v1/stores/connect/`
- **Description:** Onboard a new Shopify store after OAuth. Creates or updates a Store object and assigns a default plan.
- **Request Body:**
```json
{
  "shopify_domain": "example.myshopify.com",
  "shopify_access_token": "shpat_...",
  "email": "merchant@example.com" // optional
}
```
- **Response:**
```json
{
  "shopify_domain": "example.myshopify.com",
  "email": "merchant@example.com",
  "is_active": true,
  "current_plan": { ... },
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```
- **Logic:**
  - If the store exists, updates access token/email.
  - If not, creates a new store and assigns the first active plan as default.

#### `GET /api/v1/stores/me/`
- **Description:** Retrieve current store details (including plan info).
- **Response:**
```json
{
  "shopify_domain": "example.myshopify.com",
  "email": "merchant@example.com",
  "is_active": true,
  "current_plan": { ... },
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```

---

### 3. Subscription Management
#### `GET /api/v1/stores/me/subscription/`
- **Description:** Get the current merchant's subscription details (plan, status, usage).
- **Response:**
```json
{
  "current_plan": { ... },
  "subscription_id_external": "sub_123",
  "subscription_status": "active",
  "current_billing_period_ends": "2024-07-01T00:00:00Z",
  "current_product_count": 2,
  "current_storage_used_bytes": 123456,
  "current_month_order_count": 5,
  "last_order_count_reset_at": "2024-06-01T00:00:00Z"
}
```

#### `POST /api/v1/stores/me/subscription/`
- **Description:** Subscribe to a new plan or change the current plan.
- **Request Body:**
```json
{
  "plan_id": 2
}
```
- **Response:**
```json
{
  "current_plan": { ... },
  ...
}
```
- **Logic:**
  - Updates the store's plan and sets subscription status to active.

#### `DELETE /api/v1/stores/me/subscription/`
- **Description:** Cancel the current subscription (effective at end of billing period).
- **Response:**
```json
{
  "current_plan": { ... },
  "subscription_status": "canceled",
  ...
}
```
- **Logic:**
  - Sets subscription status to canceled.

---

### 4. Product Management
#### `POST /api/v1/products/`
- **Description:** Add a new digital product. Checks plan product count limit.
- **Request Body:**
```json
{
  "shopify_product_id": 123456,
  "shopify_variant_id": 654321,
  "name": "Ebook",
  "is_digital": true,
  "max_downloads_per_link": 5,
  "link_expiration_hours": 72
}
```
- **Response:**
```json
{
  "id": 1,
  "store": 1,
  "shopify_product_id": 123456,
  "shopify_variant_id": 654321,
  "name": "Ebook",
  "is_digital": true,
  "max_downloads_per_link": 5,
  "link_expiration_hours": 72,
  "created_at": "2024-06-01T12:00:00Z",
  "updated_at": "2024-06-01T12:00:00Z"
}
```
- **Logic:**
  - Checks if the store's product count is within plan limits before creating.

#### `GET /api/v1/products/`
- **Description:** List all digital products for the merchant.
- **Response:**
```json
[
  { ... },
  ...
]
```

#### `GET /api/v1/products/{product_id}/`
- **Description:** Retrieve details for a specific product.
- **Response:**
```json
{
  ...
}
```

#### `PUT /api/v1/products/{product_id}/`
- **Description:** Update a product's details.
- **Request Body:**
```json
{
  "name": "Updated Name"
}
```
- **Response:**
```json
{
  ...
}
```

#### `DELETE /api/v1/products/{product_id}/`
- **Description:** Delete a product. Decrements product count.
- **Response:** `204 No Content`

---

### 5. File Management (per Product)
#### `POST /api/v1/products/{product_id}/files/`
- **Description:** Upload a file for a digital product. Checks plan storage limit.
- **Request Body:**
```json
{
  "file_name": "ebook.pdf",
  "file_path": "ebooks/ebook.pdf",
  "file_size_bytes": 123456
}
```
- **Response:**
```json
{
  "id": 1,
  "product": 1,
  "file_name": "ebook.pdf",
  "file_path": "ebooks/ebook.pdf",
  "file_size_bytes": 123456,
  ...
}
```
- **Logic:**
  - Checks if the store's storage usage is within plan limits before uploading.

#### `GET /api/v1/products/{product_id}/files/`
- **Description:** List all files for a product.
- **Response:**
```json
[
  { ... },
  ...
]
```

#### `DELETE /api/v1/products/{product_id}/files/{file_id}/`
- **Description:** Delete a file. Updates storage usage.
- **Response:** `204 No Content`

---

### 6. License Key Management
#### `GET /api/v1/products/{product_id}/license-keys/`
- **Description:** List all license keys for a product.
- **Response:**
```json
[
  { ... },
  ...
]
```

#### `POST /api/v1/products/{product_id}/license-keys/`
- **Description:** Add a license key to a product.
- **Request Body:**
```json
{
  "key": "XXXX-YYYY-ZZZZ"
}
```
- **Response:**
```json
{
  "id": 1,
  "product": 1,
  "key": "XXXX-YYYY-ZZZZ",
  "is_assigned": false,
  ...
}
```

#### `DELETE /api/v1/products/{product_id}/license-keys/{key_id}/`
- **Description:** Delete a license key.
- **Response:** `204 No Content`

---

### 7. Order & Fulfillment (Shopify Webhooks)
#### `POST /api/v1/webhooks/shopify/orders/create/`
- **Description:** Receives new order notifications from Shopify. Processes digital fulfillment.
- **Request Body:**
```json
{
  "id": 123456789,
  "email": "customer@example.com",
  "line_items": [
    {
      "product_id": 123456,
      "variant_id": 654321,
      "quantity": 1
    }
  ]
}
```
- **Response:**
```json
{
  "detail": "Order processed."
}
```
- **Logic:**
  - Checks plan order limit.
  - For each digital product in the order, creates a DownloadLink and assigns a license key if available.
  - Increments store's monthly order count.

---

### 8. Customer Download
#### `GET /api/v1/download/{uuid}/`
- **Description:** Allows customers to securely download purchased files using a unique link.
- **Response:**
```json
{
  "files": [
    {
      "file_name": "ebook.pdf",
      "display_name": "Ebook PDF",
      "download_url": "https://fake-cdn.com/ebooks/ebook.pdf?token=stub"
    }
  ],
  "expires_at": "2024-06-10T12:00:00Z"
}
```
- **Logic:**
  - Validates the download link (uuid), checks expiration and download count.
  - Returns file info and (stub) download URLs.

---

## Error Handling
- Standard HTTP status codes are used (400, 401, 403, 404, 410, 422, 500, etc.).
- Error responses are JSON objects with a `detail` field describing the error.

---

## Non-Functional Notes
- File uploads and downloads are expected to use Cloudflare R2 (S3-compatible).
- Email delivery is handled by an external provider (e.g., SendGrid).
- All plan and usage limits are strictly enforced at the API level.
- All endpoints are versioned under `/api/v1/`.

---

*For further details, see the codebase and the `api_overview.md` file.* 