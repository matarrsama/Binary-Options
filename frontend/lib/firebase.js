/**
 * Firebase client configuration and initialization.
 */
import { initializeApp, getApps } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore";

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBax2xtIABQVzc_ylydg1aNcd5b8guaid4",
    authDomain: "binary-fc0fb.firebaseapp.com",
    projectId: "binary-fc0fb",
    storageBucket: "binary-fc0fb.firebasestorage.app",
    messagingSenderId: "775483971678",
    appId: "1:775483971678:web:421bf5f45c577c721ffccf",
    measurementId: "G-5YT0ZSXBSG"
};

// Initialize Firebase (only once)
let app;
let analytics;
let db;

if (typeof window !== 'undefined') {
    // Client-side initialization
    if (!getApps().length) {
        app = initializeApp(firebaseConfig);
        analytics = getAnalytics(app);
    } else {
        app = getApps()[0];
    }

    // Initialize Firestore
    db = getFirestore(app);
}

export { app, analytics, db };
