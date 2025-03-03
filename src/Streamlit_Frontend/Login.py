import streamlit as st
from database import add_user, authenticate_user  # Import from your existing database.py

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.username = username  # Store user info in session state
            st.session_state.logged_in = True
            st.success("Login successful! Redirecting to Meal Planner...")
            st.rerun()  # Reload the page to show the Meal Planner
        else:
            st.error("Invalid credentials. Please try again.")

def signup_page():
    st.title("Sign Up")
    username = st.text_input("Username")
    name = st.text_input("Full Name")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if password != confirm_password:
        st.error("Passwords do not match.")
    
    if st.button("Sign Up"):
        result = add_user(username, name, password)
        if result == "User added successfully!":
            st.success(result)
            st.session_state.username = username
            st.success("Signup successful! Please Login...")
        else:
            st.error(result)

def display_authentication_page():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        page = st.sidebar.selectbox("Select Page", ["Login", "Sign Up"])
        if page == "Login":
            login_page()
        else:
            signup_page()
