 // Import Firebase modules
 import { initializeApp } from "https://www.gstatic.com/firebasejs/11.5.0/firebase-app.js";
 import { getAuth, createUserWithEmailAndPassword,signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.5.0/firebase-auth.js";

 // Firebase configuration
 const firebaseConfig = {
     apiKey: "AIzaSyAdAFgH8J7KUE4cDINu7D3dWHXopdb59xs",
     authDomain: "healthmonitoring-5d174.firebaseapp.com",
     projectId: "healthmonitoring-5d174",
     storageBucket: "healthmonitoring-5d174.appspot.com",
     messagingSenderId: "28352098706",
     appId: "1:28352098706:web:c8b7bed6d2b596df32514b",
     measurementId: "G-5QH8P9ZRWZ"
 };

 // Initialize Firebase
 const app = initializeApp(firebaseConfig);
 const auth = getAuth(app);

 // Handle Signup Form
 document.addEventListener("DOMContentLoaded", () => {
     const signupForm = document.getElementById("signupForm");
     const loginForm = document.getElementById("loginForm");

     if (signupForm) {
         signupForm.addEventListener("submit", async (e) => {
             e.preventDefault();

             // Get user input
             const email = document.getElementById("email").value.trim();
             const password = document.getElementById("password").value.trim();

             if (!email || !password) {
                 alert("Please fill in all fields.");
                 return;
             }

             try {
                 // Create user with Firebase
                 const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                 alert("Signup successful!");
                 console.log("User created:", userCredential.user);
                 document.cookie = `user=${email}; path=/; max-age=3600`; // Set cookie for 1 hour
                 window.location.href = "/dashboard"; // Redirect after successful signup
             } catch (error) {
                 console.error("Error:", error.code, error.message);

                 let errorMessage = "Signup failed. Try again.";
                 if (error.code === "auth/email-already-in-use") {
                     errorMessage = "Email is already in use.";
                 } else if (error.code === "auth/weak-password") {
                     errorMessage = "Password should be at least 6 characters.";
                 } else if (error.code === "auth/invalid-email") {
                     errorMessage = "Invalid email format.";
                 }

                 alert(errorMessage);
             }
         });
     }
     else if (loginForm) {
      loginForm.addEventListener("submit", async (e) => {
          e.preventDefault();

          // Get user input
          const email = document.getElementById("email").value.trim();
          const password = document.getElementById("password").value.trim();

          if (!email || !password) {
              alert("Please fill in all fields.");
              return;
          }

          try {
              // Sign in user with Firebase
              const userCredential = await signInWithEmailAndPassword(auth, email, password);
              alert("Login successful!");
              console.log("User signed in:", userCredential.user);
              document.cookie = `user=${email}; path=/; max-age=3600`; 
              window.location.href = "/dashboard"; // Redirect after successful login
          } catch (error) {
              console.error("Error:", error.code, error.message);

              let errorMessage = "Login failed. Try again.";
              if (error.code === "auth/user-not-found") {
                  errorMessage = "No account found with this email.";
              } else if (error.code === "auth/wrong-password") {
                  errorMessage = "Incorrect password.";
              } else if (error.code === "auth/invalid-email") {
                  errorMessage = "Invalid email format.";
              }

              alert(errorMessage);
          }
      });
  } else {
      console.error("Login form not found.");
  }
 });