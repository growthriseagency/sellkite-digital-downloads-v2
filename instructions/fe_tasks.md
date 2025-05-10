# Frontend Development Tasks

Here are the tasks generated based on the `frontend_overview.md` document:

---

## 1. Setup Next.js Project with TypeScript
**Description:** Initialize the Next.js project with TypeScript, ESLint, and configure the basic project structure according to the PRD.
**Details:** Create a new Next.js project using \'create-next-app\' with TypeScript support. Install Next.js v15.3.2, React v18.2.0, and TypeScript v5. Configure ESLint v9 with eslint-config-next. Set up the directory structure as outlined in the PRD, creating the main folders: (app), (auth), components, lib, and styles. Initialize package.json with the correct dependencies and scripts.
**Test Strategy:** Verify that the project builds without errors. Run ESLint to ensure code quality standards are met. Check that the directory structure matches the PRD specifications.

---

## 2. Install and Configure Shopify Polaris
**Description:** Add Shopify Polaris v12.19.2 to the project and set up the theme provider for consistent styling.
**Details:** Install Shopify Polaris v12.19.2 and its dependencies. Create a theme provider in the root layout.tsx file to wrap the application. Configure global styles in styles/globals.css to work with Polaris. Import necessary Polaris CSS files. Set up any required Polaris providers like AppProvider with appropriate configurations for i18n, features, and theme.
**Test Strategy:** Verify that Polaris components render correctly with proper styling. Check that the theme is consistently applied across sample components. Ensure no console errors related to Polaris initialization.

---

## 3. Implement API Client Module
**Description:** Create a centralized API client for communicating with the backend API as specified in docs/api_docs.md.
**Details:** Develop a robust API client in lib/api.ts that handles all interactions with the backend. Implement functions for each API endpoint group mentioned in the PRD (Plans, Store Management, Subscription Management, Product Management, File Management, License Key Management). Include proper error handling, authentication token management, and request/response typing based on the API documentation. Use fetch or a library like axios for HTTP requests.
**Test Strategy:** Write unit tests for the API client functions. Mock API responses to test success and error scenarios. Verify that the client correctly formats requests and parses responses according to the API documentation.

---

## 4. Create Authentication Flow
**Description:** Implement the authentication system for Shopify OAuth connection and session management.
**Details:** Set up the authentication flow in the (auth) route group. Create the connect-shopify page to handle OAuth redirection and token exchange. Implement session management using cookies or local storage. Create API routes for auth if needed. Develop a mechanism to protect authenticated routes and redirect unauthenticated users. Consider using NextAuth.js if appropriate. Ensure the authentication flow follows the API contract for /api/v1/stores/connect/.
**Test Strategy:** Test the OAuth flow manually by simulating the Shopify connection process. Verify that authentication tokens are properly stored and used in subsequent API requests. Test protected routes to ensure they redirect unauthenticated users.

---

## 5. Implement Layout Components
**Description:** Create the main layout components including navigation, header, and sidebar for the application.
**Details:** Develop layout components in the components/layout directory. Create a Navbar component with navigation links to all main sections (Dashboard, Products, Plans, Settings). Implement a Sidebar component if needed. Design the main app layout in (app)/layout.tsx that includes these components. Use Polaris components like Navigation, TopBar, and Frame. Ensure the layout is responsive and follows Shopify design patterns.
**Test Strategy:** Test the layout components in various screen sizes to verify responsiveness. Check that navigation links work correctly. Verify that the layout renders properly with different content types.

---

## 6. Build Dashboard Page
**Description:** Create the main dashboard overview page displaying key metrics and store information.
**Details:** Implement the dashboard page at (app)/dashboard/page.tsx. Fetch store details and subscription information using the API client. Display key metrics such as current plan, storage usage, order count, and recent activity. Use Polaris components like Card, DataTable, and Banner for the UI. Implement loading states and error handling for API calls. Create any necessary dashboard-specific components in components/specific.
**Test Strategy:** Verify that the dashboard correctly displays data from the API. Test loading states and error scenarios. Check that all metrics are accurately represented and formatted properly.

---

## 7. Implement Products List Page
**Description:** Create the products list page with search, filter, and navigation capabilities.
**Details:** Build the products list page at (app)/products/page.tsx. Implement the GET /api/v1/products/ API call to fetch all products. Create a table or grid view using Polaris components like ResourceList or DataTable. Add search and filter functionality. Include pagination if needed. Add a \'New Product\' button that navigates to the product creation page. Create product card components in components/specific for displaying product information.
**Test Strategy:** Test the products list with various data scenarios (empty list, many products). Verify that search and filter functions work correctly. Check that navigation to product details and new product creation works as expected.

---

## 8. Create Product Form Components
**Description:** Develop reusable form components for product creation and editing.
**Details:** Create reusable form components in components/specific for product management. Implement form fields for all product properties (name, Shopify product/variant link, download limits, expiration, etc.). Use Polaris form components like TextField, Select, and Checkbox. Add validation logic for all fields. Create helper functions for form submission and error handling. Ensure the form components can be used for both creation and editing scenarios.
**Test Strategy:** Test form validation with various input scenarios. Verify that all form fields correctly capture and display data. Check that validation errors are properly displayed and that form submission works as expected.

---

## 9. Implement Add New Product Page
**Description:** Create the page for adding new digital products to the store.
**Details:** Build the new product page at (app)/products/new/page.tsx. Use the product form components to create a complete form for adding a new product. Implement the POST /api/v1/products/ API call for form submission. Add success and error handling for the submission process. Include a cancel button that returns to the products list. Consider adding a preview feature if applicable.
**Test Strategy:** Test the complete product creation flow from form filling to submission. Verify that the API call is made correctly and that success/error states are handled properly. Check that navigation works as expected after submission or cancellation.

---

## 10. Implement Edit Product Page
**Description:** Create the page for viewing and editing existing product details.
**Details:** Build the edit product page at (app)/products/[productId]/page.tsx. Fetch product details using GET /api/v1/products/{product_id}/. Populate the product form components with the existing data. Implement the PUT /api/v1/products/{product_id}/ API call for updating the product. Add a delete button that uses DELETE /api/v1/products/{product_id}/. Include confirmation dialogs for destructive actions. Add navigation to the files and license keys management pages.
**Test Strategy:** Test loading product data and populating the form. Verify that updates are correctly sent to the API. Test the delete functionality with confirmation. Check that navigation to related pages (files, license keys) works correctly.

---

## 11. Implement Product File Management Page
**Description:** Create the interface for uploading, viewing, and deleting files for a specific product.
**Details:** Build the file management page at (app)/products/[productId]/files/page.tsx. Implement file listing using GET /api/v1/products/{product_id}/files/. Create a file upload interface that handles the actual file upload to storage services and then calls POST /api/v1/products/{product_id}/files/ with the metadata. Add file deletion functionality using DELETE /api/v1/products/{product_id}/files/{file_id}/. Use Polaris components like ResourceList, DropZone, and Button for the UI. Implement progress indicators for uploads.
**Test Strategy:** Test file listing, uploading, and deletion. Verify that file uploads show progress and handle success/error states correctly. Check that the file list updates after operations. Test with various file types and sizes.

---

## 12. Implement License Key Management Page
**Description:** Create the interface for adding, viewing, and deleting license keys for a specific product.
**Details:** Build the license key management page at (app)/products/[productId]/license-keys/page.tsx. Implement key listing using GET /api/v1/products/{product_id}/license-keys/. Create a form for adding new keys with POST /api/v1/products/{product_id}/license-keys/. Add key deletion functionality using DELETE /api/v1/products/{product_id}/license-keys/{key_id}/. Use Polaris components like DataTable, TextField, and Button for the UI. Add bulk operations if applicable (e.g., bulk upload of keys).
**Test Strategy:** Test license key listing, adding, and deletion. Verify that the key list updates after operations. Test validation for key formats if applicable. Check that bulk operations work correctly if implemented.

---

## 13. Implement Plans and Subscription Page
**Description:** Create the page for viewing available plans, current subscription details, and managing subscriptions.
**Details:** Build the plans page at (app)/plans/page.tsx. Fetch available plans using GET /api/v1/plans/. Get current subscription details with GET /api/v1/stores/me/subscription/. Create a UI for displaying plan options and comparing features. Implement subscription management with POST /api/v1/stores/me/subscription/ for changing plans and DELETE /api/v1/stores/me/subscription/ for cancellation. Use Polaris components like Card, Banner, and Button for the UI. Add confirmation dialogs for plan changes and cancellations.
**Test Strategy:** Test plan listing and selection. Verify that current subscription details are correctly displayed. Test the plan change and cancellation flows, including confirmation dialogs. Check that the UI updates after subscription changes.

---

## 14. Implement Settings Page
**Description:** Create the settings page for viewing store information and managing store-specific settings.
**Details:** Build the settings page at (app)/settings/page.tsx. Fetch store details using GET /api/v1/stores/me/. Display store information such as name, domain, and plan details. If applicable, implement email template management based on the allow_custom_email_template flag. Use Polaris components like Card, SettingToggle, and TextField for the UI. Add any store-specific configuration options that might be available through the API.
**Test Strategy:** Verify that store information is correctly displayed. Test any editable settings to ensure they update properly. If email template management is implemented, test the template editing and preview functionality.

---

## 15. Implement Error Handling and Loading States
**Description:** Create consistent error handling and loading state components throughout the application.
**Details:** Develop reusable error handling components in components/ui. Create loading state components using Polaris SkeletonPage, SkeletonBodyText, and Spinner. Implement a global error boundary to catch unhandled exceptions. Create utility functions in lib/utils.ts for formatting error messages from the API. Ensure all API calls have proper error handling and user-friendly error messages. Add retry mechanisms for transient errors where appropriate.
**Test Strategy:** Test error handling with various error scenarios (network errors, API errors, validation errors). Verify that loading states are displayed during API calls. Check that error messages are user-friendly and actionable.

---

## 16. Implement Custom React Hooks
**Description:** Create custom React hooks for common functionality across the application.
**Details:** Identify and develop custom React hooks in lib/hooks/ for reusable logic such as managing form state, data fetching with loading/error states, or interacting with browser APIs. Ensure hooks are well-documented and tested. For example, a `useApi` hook could encapsulate common API call patterns.
**Test Strategy:** Write unit tests for custom hooks. Verify that hooks behave as expected in different scenarios and manage state correctly.

---

## 17. Ensure Frontend Responsiveness
**Description:** Ensure the application is responsive and usable across common desktop screen sizes.
**Details:** Review all pages and components for responsiveness. Use Shopify Polaris responsive props and CSS media queries where necessary. Test the application on different screen resolutions and browser window sizes.
**Test Strategy:** Manually test on various screen sizes. Use browser developer tools to simulate different devices. Verify that layouts adjust correctly and content remains readable and accessible.

---

## 18. Address Accessibility (WCAG)
**Description:** Follow WCAG guidelines to ensure the application is usable by people with disabilities.
**Details:** Leverage Shopify Polaris components' built-in accessibility features. Ensure proper ARIA attributes are used for custom components. Check for sufficient color contrast. Ensure keyboard navigability for all interactive elements.
**Test Strategy:** Use accessibility checking tools (e.g., Axe, Lighthouse). Perform keyboard-only navigation tests. Test with screen readers if possible.

--- 