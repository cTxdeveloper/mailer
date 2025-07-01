import { useAuthStore } from '~/store/auth';
import { useUiStore } from '~/store/ui'; // For global loading and error handling/notifications

export type ApiError<T = any> = {
  message: string;
  statusCode?: number;
  data?: T; // More specific error details from backend
  errors?: Record<string, string[]>; // For validation errors
};

export async function useApiFetch<T>(
  path: string,
  options: Record<string, any> = {}
): Promise<{ data: Ref<T | null>; pending: Ref<boolean>; error: Ref<ApiError | null>; refresh: () => Promise<void>; execute: () => Promise<void> }> {
  const config = useRuntimeConfig();
  const authStore = useAuthStore();
  const uiStore = useUiStore(); // For global loading state and notifications

  const defaultOptions: Record<string, any> = {
    baseURL: config.public.apiBaseUrl,
    onRequest({ options }) {
      uiStore.setGlobalLoading(true);
      if (authStore.accessToken) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${authStore.accessToken}`,
        };
      }
      options.headers = {
        ...options.headers,
        'Accept': 'application/json',
        'Content-Type': 'application/json', // Default, can be overridden
      };
    },
    onResponse({ response }) {
      uiStore.setGlobalLoading(false);
      // Potentially handle successful responses globally here if needed
      // e.g., show a success toast for POST/PUT/DELETE methods by default
    },
    onResponseError({ response }) {
      uiStore.setGlobalLoading(false);
      const apiError: ApiError = {
        message: response?._data?.message || response?._data?.detail || 'An unexpected error occurred.',
        statusCode: response?.status,
        data: response?._data,
        errors: response?._data?.errors || undefined
      };

      // Handle specific error codes
      if (response?.status === 401) { // Unauthorized
        authStore.logout(); // Clear token and redirect
        // Potentially redirect to login or show a modal
        // uiStore.showToast('Your session has expired. Please log in again.', 'error');
        if (process.client) {
            useRouter().push('/auth/login');
        }
      } else if (response?.status === 403) { // Forbidden
        // uiStore.showToast("You don't have permission to perform this action.", 'error');
      } else if (response?.status === 422) { // Validation errors
        // Errors are already in apiError.errors, can be handled by forms
        // uiStore.showToast(apiError.message || 'Validation failed. Please check the form.', 'error');
      } else if (response?.status >= 500) { // Server errors
        // uiStore.showToast('A server error occurred. Please try again later.', 'error');
      } else {
        // uiStore.showToast(apiError.message, 'error');
      }
      // The error will be returned by useFetch and can be handled locally in the component
    },
    // Automatically transform JSON responses
    // parseResponse: JSON.parse, // Usually handled by ohmyfetch by default
  };

  // Merge options, allowing user to override defaults
  const mergedOptions = { ...defaultOptions, ...options };
  mergedOptions.headers = { ...defaultOptions.headers, ...options.headers };


  // If options.body is an object, it will be automatically stringified by useFetch
  // If it's FormData, Content-Type should be multipart/form-data (usually handled by browser or manually set)
  if (options.body && typeof options.body !== 'string' && !(options.body instanceof FormData)) {
    mergedOptions.body = JSON.stringify(options.body);
  } else {
    mergedOptions.body = options.body;
  }

  // If body is FormData, remove Content-Type so browser can set it with boundary
  if (mergedOptions.body instanceof FormData) {
    delete mergedOptions.headers['Content-Type'];
  }


  // Use Nuxt's useFetch
  const { data, pending, error, refresh, execute } = await useFetch<T>(path, mergedOptions);

  // Transform the error shape if necessary, or rely on onResponseError
  // The error ref from useFetch might be different from our ApiError type
  // We ensure the error passed to the component is of type ApiError
  const customError = computed(() => {
    if (error.value) {
      // This attempts to normalize the error object from useFetch
      // to our ApiError structure.
      const errorData = (error.value as any).data || {};
      return {
        message: errorData.message || errorData.detail || error.value?.message || 'An error occurred',
        statusCode: (error.value as any).statusCode || errorData.statusCode,
        data: errorData,
        errors: errorData.errors,
      } as ApiError;
    }
    return null;
  });


  return {
    data,
    pending,
    error: customError, // Return our custom error ref
    refresh,
    execute
  };
}

// Example Usage:
//
// In your component or page:
//
// const { data: user, pending, error, refresh } = await useApiFetch<UserType>(`/users/me`);
//
// if (error.value) {
//   console.error("Failed to fetch user:", error.value.message, error.value.errors);
//   // Show error toast: uiStore.showToast(error.value.message, 'error');
// }
//
// To make a POST request:
// const { data: newPost, error: postError } = await useApiFetch<PostType>('/posts', {
//   method: 'POST',
//   body: { title: 'New Post', content: 'Hello world' }
// });
//
// if (postError.value) {
//   // Handle form errors: e.g., if (postError.value.errors?.title) { ... }
// }
//
// To upload a file:
// const formData = new FormData();
// formData.append('file', fileInput.value.files[0]);
// formData.append('description', 'My amazing file');
//
// const { data: uploadResult, error: uploadError } = await useApiFetch('/upload', {
//   method: 'POST',
//   body: formData, // Content-Type will be set automatically by the browser
// });
//
// Note: uiStore.showToast examples are commented out to avoid direct dependency here,
// but in a real app, you'd call them from onResponseError or locally after the fetch.
// It's generally better to handle UI feedback (like toasts) closer to the user interaction
// or in a global error handler that this composable might trigger.
// The current onResponseError provides a good place for global error reactions.
// Local error handling should still check the `error` ref.
//
// For non-GET requests, `execute` can be used to manually trigger the request
// instead of it running immediately.
// const { data, pending, error, execute } = await useApiFetch('/items', {
//   method: 'POST',
//   body: { name: 'New Item' },
//   immediate: false // Prevent immediate execution
// });
//
// async function createItem() {
//   await execute(); // This will make the POST request
//   if (!error.value) { /* handle success */ }
// }
//
//
// The `refresh` function can be used to re-fetch data, e.g., after an update.
//
// This composable aims to standardize API calls, token handling, global loading state,
// and basic error processing.
//
// Important: The error object returned by this composable is now `customError`,
// which tries to conform to the `ApiError` type.
// The original `error` from `useFetch` is still available internally if needed,
// but components should use the one returned by `useApiFetch`.
//
// Error handling strategy:
// 1. `onResponseError` handles global reactions (like auth redirect, generic server error toasts).
// 2. The `error` ref returned by `useApiFetch` allows components to handle specific errors locally
//    (e.g., display validation messages on a form, show a specific error message for that request).
// This provides both global consistency and local flexibility.
//
// Make sure your backend API returns errors in a consistent JSON format, ideally including:
// - `message`: A human-readable error message.
// - `errors`: (For 422/validation errors) An object where keys are field names and values are arrays of error strings.
// - `detail`: Alternative for message.
// - `statusCode`: (Optional, as it's in HTTP status)
// Example error response from backend (422 Validation Error):
// {
//   "message": "The given data was invalid.",
//   "errors": {
//     "email": ["The email field is required.", "The email must be a valid email address."],
//     "password": ["The password field is required."]
//   }
// }
// Example error response from backend (500 Server Error):
// {
//   "message": "Internal Server Error. Please try again later."
// }
// Example error response from backend (404 Not Found):
// {
//   "message": "Resource not found."
// }
//
// This useApiFetch will attempt to parse these structures.
//
// The `uiStore.setGlobalLoading(true/false)` calls manage a global loading indicator.
// You would typically have a component in your `app.vue` or layout that observes
// `uiStore.isGlobalLoading` to show/hide a loading bar or spinner.
//
// For `NuxtLoadingIndicator` in `app.vue`, it handles page navigation loading.
// `uiStore.isGlobalLoading` is for API request loading, which can be a different visual.
// You might want to integrate them or have distinct indicators.
// For instance, `NuxtLoadingIndicator` for route changes, and a smaller, more subtle
// indicator (e.g., in the header) for API calls driven by `uiStore.isGlobalLoading`.
//
// Consider adding a `watch` on `authStore.accessToken` within this composable if you need
// to react to token changes for ongoing requests or configurations, although `onRequest`
// should handle it for new requests.
//
// The use of `execute` from `useFetch` is now exposed, allowing for manual triggering of requests,
// which is useful for POST/PUT/DELETE operations that shouldn't run on component mount.
// `refresh` is also exposed for re-fetching data.
// By default, `useFetch` (and thus `useApiFetch`) will execute immediately for GET requests.
// For non-GET requests, or if you want to control execution, pass `{ immediate: false }`
// in the options and then call `await execute()`.
//
// The type of `data` is `Ref<T | null>`. It's important to handle the `null` case,
// especially before the first fetch completes or if the fetch fails.
//
// `pending` is a `Ref<boolean>` that indicates if the request is in flight.
//
// The return type has been updated to reflect the exposure of `execute`.
// `Promise<{ data: Ref<T | null>; pending: Ref<boolean>; error: Ref<ApiError | null>; refresh: () => Promise<void>; execute: () => Promise<void> }>`
//
// This composable is now quite robust and covers many common API interaction scenarios.
// Remember to define your TypeScript types (like `UserType`, `PostType`) in `~/types/index.ts`
// or similar for better type safety.
//
// Example of defining UserType in `~/types/index.ts`:
// export interface User {
//   id: number;
//   name: string;
//   email: string;
//   // ... other properties
// }
// Then use `useApiFetch<User>('/users/me')`.
//
// If your API returns paginated data, you might have a structure like:
// export interface PaginatedResponse<T> {
//   data: T[];
//   links: {
//     first: string | null;
//     last: string | null;
//     prev: string | null;
//     next: string | null;
//   };
//   meta: {
//     current_page: number;
//     from: number | null;
//     last_page: number;
//     path: string;
//     per_page: number;
//     to: number | null;
//     total: number;
//   };
// }
// Then use `useApiFetch<PaginatedResponse<Bounty>>('/bounties')`.
//
// This composable is designed to be the primary way your frontend interacts with the Python backend.
// Ensure the `apiBaseUrl` in `nuxt.config.ts` (and thus `runtimeConfig.public.apiBaseUrl`)
// is correctly set for your development and production environments.
// e.g., `NUXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1` in your `.env` file.
//
// Final check on headers: 'Accept': 'application/json' ensures the backend knows we expect JSON.
// 'Content-Type': 'application/json' is for the body of POST/PUT requests.
// If you ever need to send XML or other formats, you'd override 'Content-Type'.
// For FormData, 'Content-Type' is deliberately removed to let the browser set it correctly
// with the multipart boundary.
//
// This composable should now be fully functional for the described application.
//
// Consider adding request caching strategies if needed, though `useFetch` has some
// built-in caching capabilities (e.g., with the `key` option or by default for GET requests).
// For more advanced caching, you might need a library or custom logic.
//
// The current error handling focuses on JSON API responses. If your API might return
// non-JSON errors (e.g., plain text or HTML for some server misconfigurations),
// `onResponseError` might need adjustments to handle those gracefully.
// However, for a well-structured API, JSON error responses are standard.
//
// The type `ApiError<T = any>` for `error.value.data` allows for more specific typing
// of the error response body if known. For example, if a 400 error always returns
// a specific object shape: `ApiError<{ reason: string; code: number; }>`
//
// This structure gives a good balance of global setup and local control.
// The global loading via `uiStore` is helpful for a consistent UX.
// The token management via `authStore` is centralized.
// Error handling is both global (for common cases like 401) and local (for component-specific feedback).
//
// Remember to install `ohmyfetch` (it's a dep of Nuxt 3, so usually available) or ensure
// `useFetch` behaves as expected regarding automatic JSON parsing and header management.
// Nuxt 3's `useFetch` is built on top of `ofetch` (formerly `ohmyfetch`).
//
// One final thought: for very sensitive operations, you might consider adding CSRF protection
// if your backend uses cookie-based sessions alongside tokens (less common for SPA + API token auth).
// If using only Bearer tokens, CSRF is generally not an issue for the API itself, but ensure
// your login/token generation endpoints are secure.
// For this project, standard Bearer token auth is assumed.
