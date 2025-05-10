## 1. Introduction

This document outlines the product requirements and technical overview for the frontend of the Digital Downloads application. The frontend will provide Shopify merchants with a user interface to manage their digital products, subscriptions, and view sales data, interacting with the backend API documented in `docs/api_docs.md`.

---

## 2. Core Technologies & Libraries

The frontend will be built using the following technologies:

*   **Framework:** Next.js (v15.3.2) - For server-side rendering, routing, and overall application structure.
*   **UI Library:** React (v18.2.0) - For building interactive user interfaces.
*   **Styling & Components:** Shopify Polaris (v12.19.2) - To ensure a consistent look and feel with the Shopify ecosystem.
*   **Language:** TypeScript (v5) - For type safety and improved developer experience.
*   **Linting:** ESLint (v9) - Configured with `eslint-config-next` for code quality.

*(Dependency versions sourced from `frontend/src/package.json`)*

---

## 3. Proposed Directory Structure (within `frontend/src/app`)

Given the Next.js App Router structure, we will organize pages and components as follows:

```
frontend/src/app/
├── (app)/                        # Logged-in merchant experience
│   ├── dashboard/
│   │   └── page.tsx              # Main dashboard overview
│   ├── products/
│   │   ├── page.tsx              # List products
│   │   ├── [productId]/
│   │   │   ├── page.tsx          # View/Edit product details
│   │   │   └── files/
│   │   │       └── page.tsx      # Manage files for a product
│   │   │   └── license-keys/
│   │   │       └── page.tsx      # Manage license keys for a product
│   │   └── new/
│   │       └── page.tsx          # Add new product
│   ├── plans/
│   │   └── page.tsx              # View available plans, manage subscription
│   ├── settings/
│   │   └── page.tsx              # Store settings (e.g., email templates if applicable)
│   └── layout.tsx                # Main app layout (nav, header)
│
├── (auth)/                       # Authentication pages
│   ├── connect-shopify/
│   │   └── page.tsx              # Shopify OAuth connection handler/landing
│   └── login/
│       └── page.tsx              # (If we implement a separate login beyond Shopify)
│
├── api/                          # Next.js API routes (if any needed on frontend side)
│   └── auth/
│       └── [...nextauth]/route.ts # Example if using NextAuth.js
│
├── components/                   # Shared UI components
│   ├── layout/                   # Layout specific components (e.g., Navbar, Sidebar)
│   ├── ui/                       # Generic, reusable UI elements (e.g., Button, Card, Modal)
│   └── specific/                 # Components specific to a feature/domain (e.g., ProductCard, PlanSelector)
│
├── lib/                          # Utility functions, API client, hooks
│   ├── api.ts                    # Centralized API client for backend communication
│   ├── hooks/                    # Custom React hooks
│   └── utils.ts                  # General utility functions
│
├── styles/                       # Global styles, theme configurations
│   └── globals.css
│
└── layout.tsx                    # Root layout
└── page.tsx                      # Landing page / Public homepage (if any)
```

**Rationale:**

*   **Route Groups `(app)` and `(auth)`:** Separate logged-in user routes from authentication/public routes.
*   **Feature-based routing:** Under `(app)`, routes are grouped by major features (dashboard, products, plans, settings) as suggested by the API structure.
*   **Nested routes for details/actions:** e.g., `products/[productId]` for viewing/editing a specific product.
*   **`components/` directory:**
    *   `layout/`: For components specifically tied to the main application layout.
    *   `ui/`: For generic, highly reusable components (atoms/molecules in atomic design).
    *   `specific/`: For more complex components that are tied to a particular feature but might be used in multiple places within that feature's context.
*   **`lib/` directory:** For core logic, API interaction, custom hooks, and general utilities, promoting separation of concerns.

---

## 4. API Interaction Summary

The frontend will interact with the backend API (documented in `docs/api_docs.md`). Key areas of interaction include:

**API Contract Enforcement:**
*   **ALWAYS reference `docs/api_docs.md` for every API call.**
*   **Verify:**
    *   The endpoint URL and HTTP method match the documentation.
    *   The request payload (body, query params, headers) matches the documented schema.
    *   The response structure matches the documentation.
    *   The status codes and error payloads are handled as described.
    *   Authentication requirements are respected as documented.
*   If any discrepancy is found, pause implementation and resolve the mismatch.

**Key API Endpoint Groups to be Consumed:**

1.  **Plan Management (`/api/v1/plans/`)**
    *   `GET /api/v1/plans/`: To display available subscription plans to merchants.

2.  **Store Management & Onboarding**
    *   `POST /api/v1/stores/connect/`: For initial store setup after Shopify OAuth.
    *   `GET /api/v1/stores/me/`: To fetch current store details and plan information for display in settings or dashboard.

3.  **Subscription Management (`/api/v1/stores/me/subscription/`)**
    *   `GET /api/v1/stores/me/subscription/`: To display current subscription status, usage metrics (product count, storage, orders).
    *   `POST /api/v1/stores/me/subscription/`: To allow merchants to select or change their subscription plan.
    *   `DELETE /api/v1/stores/me/subscription/`: To allow merchants to cancel their subscription.

4.  **Product Management (`/api/v1/products/...`)**
    *   `POST /api/v1/products/`: To create new digital products.
    *   `GET /api/v1/products/`: To list all products for the merchant.
    *   `GET /api/v1/products/{product_id}/`: To view details of a specific product.
    *   `PUT /api/v1/products/{product_id}/`: To update product details.
    *   `DELETE /api/v1/products/{product_id}/`: To delete products.

5.  **File Management (per Product) (`/api/v1/products/{product_id}/files/...`)**
    *   `POST /api/v1/products/{product_id}/files/`: To upload files associated with a product. (Note: Frontend will need to handle actual file upload to a service like S3/R2, then pass metadata to this endpoint).
    *   `GET /api/v1/products/{product_id}/files/`: To list files for a product.
    *   `DELETE /api/v1/products/{product_id}/files/{file_id}/`: To delete files.

6.  **License Key Management (`/api/v1/products/{product_id}/license-keys/...`)**
    *   `GET /api/v1/products/{product_id}/license-keys/`: To list license keys for a product.
    *   `POST /api/v1/products/{product_id}/license-keys/`: To add new license keys.
    *   `DELETE /api/v1/products/{product_id}/license-keys/{key_id}/`: To delete license keys.

*(Note: Order & Fulfillment and Customer Download endpoints are primarily webhook/backend or public-facing and may have less direct UI in the merchant admin frontend, but data derived from them might be displayed, e.g., order counts).*

---

## 5. Key Frontend Pages/Views (Mapping to Directory Structure)

*   **Dashboard (`/dashboard`):** Overview of key metrics (e.g., current plan, storage usage, order count, recent activity).
*   **Products List (`/products`):** Table/grid view of all digital products. Ability to search, filter, and navigate to add/edit products.
*   **Add/Edit Product (`/products/new`, `/products/[productId]`):** Forms for creating and updating product details (name, Shopify product/variant link, download limits, expiration).
*   **Product File Management (`/products/[productId]/files`):** Interface to upload, view, and delete files for a specific product.
*   **Product License Key Management (`/products/[productId]/license-keys`):** Interface to add, view, and delete license keys for a specific product.
*   **Plans & Subscription (`/plans`):** Display available plans, current subscription details, usage against limits. Allow plan selection/change and cancellation.
*   **Settings (`/settings`):** View store information, potentially manage email templates (if `allow_custom_email_template` is true and implemented).
*   **Shopify Connect (`/(auth)/connect-shopify`):** Page to handle post-OAuth logic, potentially showing a success/failure message.

---

## 6. Non-Functional Requirements

*   **Responsiveness:** The application should be responsive and usable across common desktop screen sizes.
*   **Performance:** Pages should load quickly, and interactions should feel snappy. Optimize API calls and client-side rendering.
*   **Accessibility:** Follow WCAG guidelines to ensure the application is usable by people with disabilities. Shopify Polaris components assist with this.
*   **Error Handling:** Clearly display errors from API calls or client-side issues, providing user-friendly messages.
*   **Security:**
    *   Protect against common web vulnerabilities (XSS, CSRF). Next.js and React provide some built-in protections.
    *   Handle authentication tokens securely.

---

This PRD will be updated as the project progresses and new requirements emerge. 