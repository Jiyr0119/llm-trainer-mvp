<template>
    <div>
        <NuxtPage />
        <UNotifications />
    </div>
</template>

<script setup>
// Set page title
useHead({
    htmlAttrs: {
        lang: 'zh-CN'
    },
    link: [
        {
            rel: 'preconnect',
            href: 'https://fonts.googleapis.com'
        },
        {
            rel: 'preconnect',
            href: 'https://fonts.gstatic.com',
            crossorigin: ''
        },
        {
            rel: 'stylesheet',
            href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap'
        }
    ]
});
</script>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html,
body {
    height: 100%;
    width: 100%;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body {
    @apply bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-white;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    @apply bg-gray-100 dark:bg-gray-900;
}

::-webkit-scrollbar-thumb {
    @apply bg-gray-300 dark:bg-gray-700 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
    @apply bg-gray-400 dark:bg-gray-600;
}
</style>
