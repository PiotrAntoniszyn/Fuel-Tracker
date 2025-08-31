"""
Streamlit configuration for PWA functionality
"""

import streamlit as st

def configure_pwa():
    """Configure Streamlit for PWA functionality"""
    
    # Add manifest and meta tags for PWA
    st.markdown("""
    <link rel="manifest" href="./manifest.json">
    <meta name="theme-color" content="#ff6b6b">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Fuel Tracker">
    
    <!-- Service Worker Registration -->
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('./sw.js')
                    .then(function(registration) {
                        console.log('SW registered: ', registration);
                    }, function(registrationError) {
                        console.log('SW registration failed: ', registrationError);
                    });
            });
        }
    </script>
    """, unsafe_allow_html=True)