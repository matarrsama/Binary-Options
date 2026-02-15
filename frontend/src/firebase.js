import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAnalytics } from 'firebase/analytics';

const firebaseConfig = {
  apiKey: "AIzaSyBax2xtIABQVzc_ylydg1aNcd5b8guaid4",
  authDomain: "binary-fc0fb.firebaseapp.com",
  projectId: "binary-fc0fb",
  storageBucket: "binary-fc0fb.firebasestorage.app",
  messagingSenderId: "775483971678",
  appId: "1:775483971678:web:421bf5f45c577c721ffccf",
  measurementId: "G-5YT0ZSXBSG"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const firestore = getFirestore(app);

export { firestore, app, analytics };
