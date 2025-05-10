**1. Introduction**

This document outlines the requirements for a RESTful API that enables Shopify merchants to offer digital download delivery for their products. When an order containing a designated digital product is placed, the API will facilitate sending an email to the customer with a unique link to access their purchased files and any associated license keys. The service will offer tiered paid plans, imposing limits on usage based on the selected plan, and will be built entirely on the DigitalOcean cloud platform.

**2. Goals**

* **Enable Digital Product Delivery:** Allow merchants to easily attach digital files and license keys to their Shopify products/variants.
* **Automate Fulfillment:** Automatically detect orders requiring digital delivery and trigger the sending of download links.
* **Secure Access:** Ensure that only legitimate customers can access their purchased digital files.
* **Scalability & Efficiency:** Build the API using Django Rest Framework (DRF) and PostgreSQL on DigitalOcean to handle a growing number of merchants, products, and orders efficiently.
* **Merchant Self-Service:** Provide merchants with an interface (via API or a separate merchant-facing app consuming this API) to manage their digital products, files, licenses, and subscription plans.
* **Monetization:** Implement a subscription-based model with tiered plans offering varying levels of features and usage limits (e.g., number of products, orders processed, storage).

**3. User Stories**

* **As a Merchant, I want to:**
    * Connect my Shopify store to the digital downloads app.
    * View available subscription plans and their features/limits (products, orders, storage).
    * Choose and subscribe to a suitable plan.
    * Upgrade or downgrade my plan.
    * Be clearly informed when I am approaching or have reached my plan limits.
    * Designate specific Shopify products or variants as digital products (up to my plan's limit).
    * Upload multiple files for each digital product (within my plan's storage limit).
    * Add multiple license keys for each digital product.
    * View a list of my digital products and their associated files/licenses.
    * Edit or remove files and license keys associated with my products.
    * See a log of digital deliveries made (up to my plan's order limit).
    * Customize the email template used for sending download links (potentially a premium feature).
* **As a Customer, I want to:**
    * Receive an email with a unique and secure link to download my purchased digital files after completing an order.
    * Access any license keys associated with my purchase.
    * Be able to download the files multiple times within a reasonable limit or timeframe (merchant configurable).
* **As an Admin (App Developer), I want to:**
    * Define and manage different subscription plans (name, price, limits for products, orders, storage).
    * Monitor the health and usage of the API.
    * Manage merchant accounts and their subscription status.
    * Track merchant usage against their plan limits.
    * Troubleshoot delivery issues.
    * Integrate with a payment gateway to handle subscriptions.

**4. System Architecture Overview**

The system will consist of:

* **Shopify Store:** The merchant's e-commerce platform.
* **Shopify Webhooks:** Used to notify our API about new orders.
* **Digital Downloads API (DRF on DigitalOcean):** The core application responsible for:
    * Storing merchant information, plan subscriptions, and product-file mappings.
    * Managing subscription plans and tracking usage against limits.
    * Receiving order information from Shopify.
    * Processing orders to identify digital products, respecting plan limits.
    * Generating secure download links.
    * Managing file storage on **DigitalOcean Spaces**.
    * Managing license key distribution.
    * Triggering email notifications via an **external email service provider** (e.g., SendGrid, Mailgun, Postmark, integrated with the application running on DigitalOcean).
* **PostgreSQL Database (DigitalOcean Managed Database):** Stores all application data.
* **Email Service:** (e.g., SendGrid, Mailgun, Postmark) To send download emails.
* **Payment Gateway:** (e.g., Stripe, Paddle) For handling plan subscriptions.
* **(Optional) Merchant Facing UI:** A web application that consumes the API.

**5. Database Schema (PostgreSQL)**

*Added tables/fields are marked with `*` or detailed in descriptions.*

* **`Plan`***
    * `id`: `SERIAL PRIMARY KEY`
    * `name`: `VARCHAR(100) UNIQUE NOT NULL` (e.g., "Basic", "Pro", "Unlimited")
    * `price_monthly`: `DECIMAL(10, 2) NOT NULL`
    * `price_annually`: `DECIMAL(10, 2)` (Optional)
    * `max_products`: `INTEGER` (NULL for unlimited)
    * `max_orders_per_month`: `INTEGER` (NULL for unlimited)
    * `max_storage_gb`: `INTEGER` (NULL for unlimited)
    * `allow_custom_email_template`: `BOOLEAN DEFAULT FALSE`
    * `is_active`: `BOOLEAN DEFAULT TRUE` (Can be deactivated)
    * `created_at`: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`
    * `updated_at`: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`

* **`Store`**
    * `id`: `SERIAL PRIMARY KEY`
    * `shopify_domain`: `VARCHAR(255) UNIQUE NOT NULL`
    * `shopify_access_token`: `VARCHAR(255) NOT NULL` (encrypted)
    * `email`: `VARCHAR(255)`
    * `is_active`: `BOOLEAN DEFAULT TRUE`
    * `current_plan_id`\*: `INTEGER REFERENCES Plan(id) ON DELETE SET NULL` (Can be NULL if no active plan, or on a free/trial tier not explicitly in `Plan` table)
    * `subscription_id_external`\*: `VARCHAR(255)` (e.g., Stripe Subscription ID)
    * `subscription_status`\*: `VARCHAR(50)` (e.g., `active`, `canceled`, `past_due`)
    * `current_billing_period_ends`\*: `TIMESTAMP WITH TIME ZONE`
    * `created_at`: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`
    * `updated_at`: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`
    * `current_product_count`\*: `INTEGER DEFAULT 0` (For tracking against `Plan.max_products`)
    * `current_storage_used_bytes`\*: `BIGINT DEFAULT 0` (For tracking against `Plan.max_storage_gb`)
    * `current_month_order_count`\*: `INTEGER DEFAULT 0` (Resets monthly, for tracking against `Plan.max_orders_per_month`)
    * `last_order_count_reset_at`\*: `TIMESTAMP WITH TIME ZONE`

* **`Product`**
    * `id`: `SERIAL PRIMARY KEY`
    * `store_id`: `INTEGER REFERENCES Store(id) ON DELETE CASCADE NOT NULL`
    * `shopify_product_id`: `BIGINT NOT NULL`
    * `shopify_variant_id`: `BIGINT UNIQUE`
    * `name`: `VARCHAR(255)`
    * `is_digital`: `BOOLEAN DEFAULT TRUE`
    * `max_downloads_per_link`: `INTEGER DEFAULT 5`
    * `link_expiration_hours`: `INTEGER DEFAULT 72`
    * `created_at`: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`
    * `updated_at`: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`
    * `UNIQUE (store_id, shopify_product_id, shopify_variant_id)`

* **`File`**
    * `id`: `SERIAL PRIMARY KEY`
    * `product_id`: `INTEGER REFERENCES Product(id) ON DELETE CASCADE NOT NULL`
    * `file_name`: `VARCHAR(255) NOT NULL`
    * `file_path`: `VARCHAR(1024) NOT NULL` (Path in **DigitalOcean Spaces**)
    * `file_type`: `VARCHAR(50)`
    * `file_size_bytes`: `BIGINT NOT NULL`
    * `display_name`: `VARCHAR(255)`
    * `upload_date`: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`
    * `updated_at`: `TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`

* **`LicenseKey`** (Schema remains the same)
    * ...

* **`Order`** (Schema remains the same)
    * ...

* **`OrderItem`** (Schema remains the same)
    * ...

* **`DownloadLink`** (Schema remains the same, ensure `uuid-ossp` extension is enabled)
    * ...

* **`AssignedLicenseKey`** (Schema remains the same)
    * ...

**Logic for Usage Tracking:**
* When a `Product` is created, increment `Store.current_product_count`.
* When a `File` is uploaded, add its `file_size_bytes` to `Store.current_storage_used_bytes`.
* When an `Order` is processed successfully via webhook, increment `Store.current_month_order_count`. A periodic task (e.g., daily or at the start of a request) should check `Store.last_order_count_reset_at` to reset `current_month_order_count` if a new billing month has started.
* Deleting products/files should decrement respective counts/storage.

**6. API Endpoints (DRF)**

*Authentication: All merchant-facing endpoints require authentication.*
*Plan Limit Checks: Endpoints creating resources (products, files) or processing orders must check against the merchant's current plan limits.*

**6.1. Plan Endpoints (Public/Merchant Facing)**

* **`GET /api/v1/plans/`***
    * **Description:** List all available active subscription plans.
    * **Response:** `200 OK` List of plan details.

**6.2. Subscription Endpoints (Merchant Facing)**

* **`GET /api/v1/stores/me/subscription/`***
    * **Description:** Get the current merchant's subscription details (current plan, status, usage).
    * **Response:** `200 OK` Subscription and usage details.
* **`POST /api/v1/stores/me/subscription/`***
    * **Description:** Merchant subscribes to a new plan or changes their plan. This would typically involve redirecting to a payment provider (e.g., Stripe Checkout session) or handling payment details. The API would then update the subscription status based on webhook feedback from the payment provider.
    * **Request Body:** `{ "plan_id": 1, "payment_token": "tok_..." (if applicable) }`
    * **Response:** `200 OK` or `202 Accepted` with next steps (e.g., redirect URL for payment).
* **`DELETE /api/v1/stores/me/subscription/`***
    * **Description:** Merchant cancels their subscription (effective at the end of the current billing period).
    * **Response:** `200 OK` Confirmation of cancellation request.

**6.3. Store Endpoints** (Modified for plan awareness)

* **`POST /api/v1/stores/connect/`**
    * **Description:** ... (Upon successful connection, the merchant might be placed on a default free/trial plan or prompted to select a plan).
    * ...
* **`GET /api/v1/stores/me/`** (No change in basic structure, but response might include plan info indirectly or via a nested subscription object)

**6.4. Product Endpoints (Merchant Facing)**

* **`POST /api/v1/products/`**
    * **Description:** Merchant adds a new digital product.
        * **Plan Limit Check:** Verify if `Store.current_product_count < Plan.max_products`.
    * **Response:** `201 Created` or `402 Payment Required`/`403 Forbidden` if limit exceeded.
    * *(On success, increment `Store.current_product_count`)*
* **`GET /api/v1/products/`** (No change)
* **`GET /api/v1/products/{product_id}/`** (No change)
* **`DELETE /api/v1/products/{product_id}/`**
    * *(On success, decrement `Store.current_product_count`)*
    * **Response:** `204 No Content`.

**6.5. File Endpoints (Merchant Facing, under a Product)**

* **`POST /api/v1/products/{product_id}/files/`**
    * **Description:** Upload a file for a digital product.
        * **Plan Limit Check:** Verify if `Store.current_storage_used_bytes + new_file_size < Plan.max_storage_gb * 1024^3`.
    * **Response:** `201 Created` or `402 Payment Required`/`403 Forbidden` if limit exceeded.
    * *(On success, update `Store.current_storage_used_bytes` and store file in **DigitalOcean Spaces**)*
* **`GET /api/v1/products/{product_id}/files/`** (No change)
* **`DELETE /api/v1/products/{product_id}/files/{file_id}/`**
    * *(On success, update `Store.current_storage_used_bytes` and delete file from **DigitalOcean Spaces**)*
    * **Response:** `204 No Content`.

**6.6. License Key Endpoints** (No direct plan limits typically, but product count limit applies)
* ... (Endpoints remain the same)

**6.7. Shopify Webhook Endpoints (Internal - called by Shopify)**

* **`POST /api/v1/webhooks/shopify/orders/create/`**
    * **Description:** Receives new order notifications from Shopify.
    * **Plan Limit Check:** Before full processing, verify if `Store.current_month_order_count < Plan.max_orders_per_month`. If the store is over its limit, the order might be logged but not fulfilled, or the merchant is notified. This behavior needs careful definition (e.g., allow overage for a fee, or hard stop).
    * **Logic:**
        * ...
        * If plan limit is okay:
            * Process order, create `DownloadLink`, send email.
            * Increment `Store.current_month_order_count`.
        * Else (limit exceeded):
            * Log the issue.
            * Optionally notify the merchant.
            * Do not fulfill the digital part via the app.
    * **Response:** `200 OK`.

**6.8. Customer Download Endpoints** (No change)
* ... (Endpoints remain the same, file serving from **DigitalOcean Spaces** via pre-signed URLs or streaming through the app)

**7. Non-Functional Requirements**

* **Security:** (As before)
* **Scalability:**
    * API and background workers deployed on **DigitalOcean Droplets** or **DigitalOcean Kubernetes Service (DOKS)**.
    * Utilize **DigitalOcean Managed PostgreSQL** for database scalability.
    * Utilize **DigitalOcean Managed Redis** for Celery broker and caching.
    * Asynchronous task queues (Celery) are crucial.
* **Performance:**
    * File downloads from **DigitalOcean Spaces**, potentially using its CDN capabilities or generating pre-signed URLs.
* **Reliability:** (As before, with DigitalOcean infrastructure)
* **Maintainability:** (As before)
* **Monitoring & Logging:** (As before, potentially using DigitalOcean monitoring or self-hosted solutions like Prometheus/Grafana on Droplets).

**8. Technology Stack (DigitalOcean Focused)**

* **Backend:** Python, Django, Django Rest Framework (DRF)
* **Database:** **DigitalOcean Managed PostgreSQL**
* **Compute/Deployment:** **DigitalOcean Droplets** (VMs) or **DigitalOcean Kubernetes (DOKS)**. Use Docker for containerization.
* **Task Queue:** Celery with **DigitalOcean Managed Redis** (as broker and results backend).
* **Caching:** **DigitalOcean Managed Redis**.
* **File Storage:** **DigitalOcean Spaces** (S3-compatible object storage).
* **Email Service:** External provider like SendGrid, Mailgun, Postmark. (Avoid self-hosting email on a Droplet for production due to deliverability challenges).
* **Payment Gateway Integration:** Stripe, Paddle, or similar.
* **CI/CD:** Tools like GitLab CI/CD, GitHub Actions, Jenkins deploying to DigitalOcean.

**9. Future Considerations**

* **Merchant Dashboard:** (As before)
* **Download Tracking & Analytics:** (As before)
* **Billing Management UI:** Interface for merchants to manage their payment methods and view invoices (often provided by the payment gateway but needs integration).
* **Trial Periods:** Formal support for trial periods before paid subscription starts.
* **Overage Charges:** Option for merchants to pay for usage beyond their plan limits instead of a hard stop.
* ... (Other previous future considerations still apply)

## ✅ Implemented API Endpoints (as of code review)

- GET /api/v1/plans/ ✅
- GET /api/v1/stores/me/subscription/ ✅
- POST /api/v1/stores/me/subscription/ ✅
- DELETE /api/v1/stores/me/subscription/ ✅
- GET /api/v1/stores/me/ ✅
- POST /api/v1/products/ ✅
- GET /api/v1/products/ ✅
- GET /api/v1/products/{product_id}/ ✅
- DELETE /api/v1/products/{product_id}/ ✅
- POST /api/v1/products/{product_id}/files/ ✅
- GET /api/v1/products/{product_id}/files/ ✅
- DELETE /api/v1/products/{product_id}/files/{file_id}/ ✅
- License Key Endpoints (add, list, delete, assign, etc.) ✅
- POST /api/v1/webhooks/shopify/orders/create/ ✅
- POST /api/v1/stores/connect/ (Store onboarding) ✅
- Customer Download Endpoints (for secure file access by customers) ✅
