"""
Simple authentication module for Fuel Tracker
"""

import streamlit as st
from supabase import Client
import hashlib
import secrets

class SimpleAuth:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        calculated_hash, _ = self.hash_password(password, salt)
        return calculated_hash == password_hash
    
    def register_user(self, email: str, password: str) -> bool:
        """Register a new user (simplified - for single user)"""
        try:
            # For MVP, we'll use Supabase Auth
            result = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if result.user:
                st.success("Registration successful! Please check your email for verification.")
                return True
            else:
                st.error("Registration failed")
                return False
                
        except Exception as e:
            st.error(f"Registration error: {str(e)}")
            return False
    
    def login_user(self, email: str, password: str) -> bool:
        """Login user"""
        try:
            result = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if result.user:
                st.session_state['authenticated'] = True
                st.session_state['user'] = result.user
                return True
            else:
                st.error("Invalid credentials")
                return False
                
        except Exception as e:
            st.error(f"Login error: {str(e)}")
            return False
    
    def logout_user(self):
        """Logout user"""
        try:
            self.supabase.auth.sign_out()
            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            st.rerun()
        except Exception as e:
            st.error(f"Logout error: {str(e)}")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def require_auth(self):
        """Decorator to require authentication"""
        if not self.is_authenticated():
            self.show_login_form()
            st.stop()
    
    def show_login_form(self):
        """Show login/register form"""
        st.title("🔐 Fuel Tracker Login")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login", use_container_width=True):
                    if email and password:
                        if self.login_user(email, password):
                            st.rerun()
                    else:
                        st.error("Please fill in all fields")
        
        with tab2:
            st.subheader("Register")
            with st.form("register_form"):
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
                
                if st.form_submit_button("Register", use_container_width=True):
                    if reg_email and reg_password and reg_password_confirm:
                        if reg_password != reg_password_confirm:
                            st.error("Passwords don't match")
                        elif len(reg_password) < 6:
                            st.error("Password must be at least 6 characters")
                        else:
                            self.register_user(reg_email, reg_password)
                    else:
                        st.error("Please fill in all fields")
        
        st.info("💡 For MVP testing, you can create a single account for personal use.")