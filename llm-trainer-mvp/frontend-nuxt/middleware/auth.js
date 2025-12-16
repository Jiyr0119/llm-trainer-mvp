// Auth middleware to protect routes
export default defineNuxtRouteMiddleware((to, from) => {
    // Skip auth check on server side
    if (process.server) return;

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/register'];

    // Check if route is public
    if (publicRoutes.includes(to.path)) {
        return;
    }

    // Check if user is authenticated
    const token = localStorage.getItem('access_token');

    if (!token) {
        // Redirect to login if not authenticated
        return navigateTo('/login');
    }
});
