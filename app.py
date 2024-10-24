import streamlit as st
from chatbot import handle_user_query, create_database, save_file_to_db, process_zip_folder, register_user, \
    authenticate_user

# Create a session state for storing query history and user role
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

# Define the database path
DB_PATH = "database/database2.db"


def apply_default_theme():
    pass


# Add scrolling title with CSS
def add_scrolling_title():
    st.markdown("""
        <style>
            @keyframes scroll {
                0% { transform: translateX(100%); }
                100% { transform: translateX(-100%); }
            }
            .scrolling-title {
                white-space: nowrap;
                overflow: hidden;
                box-sizing: border-box;
            }
            .scrolling-title div {
                display: inline-block;
                padding-left: 100%;
                animation: scroll 10s linear infinite;
            }
        </style>
        <div class="scrolling-title">
            <div>LEGAL PREDICT IQ - AI-Driven Legal Analysis</div>
        </div>
    """, unsafe_allow_html=True)


def main():
    # Create the database and the "Files" table if they don't exist
    create_database()

    # Apply default theme to the entire application
    apply_default_theme()

    # Scrolling title
    add_scrolling_title()

    st.title("LEGAL PREDICT IQ")

    # Sidebar section for user actions
    st.sidebar.header("User Actions")
    action = st.sidebar.selectbox("Select an option", ["User Login", "Admin Login", "Register"])

    if action == "User Login":
        user_login()
    elif action == "Admin Login":
        admin_login()
    elif action == "Register":
        user_registration()

    # User query section
    if st.session_state.user_authenticated:
        st.header("Ask a Legal Question")
        user_query = st.text_input("Enter your question here:")

        if st.button("Get Answer"):
            if user_query:
                st.session_state.query_history.append(user_query)
                with st.spinner("Retrieving answer..."):
                    answer = handle_user_query(user_query)
                    st.success(answer)
            else:
                st.error("Please enter a question.")

    # Admin dashboard section
    if st.session_state.admin_authenticated:
        admin_dashboard()


def user_login():
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if authenticate_user(username, password):
            st.session_state.user_authenticated = True
            st.success("Logged in successfully.")
        else:
            st.error("Invalid username or password.")


def user_registration():
    full_name = st.sidebar.text_input("Full Name")
    username = st.sidebar.text_input("Username")
    phone_number = st.sidebar.text_input("Phone Number")
    email = st.sidebar.text_input("Email")
    profession = st.sidebar.selectbox("Profession", ["Lawyer", "Law Research Student", "Other"])
    if profession == "Other":
        profession = st.sidebar.text_input("Please specify your profession")
    password = st.sidebar.text_input("Password", type="password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")

    if st.sidebar.button("Register"):
        if password == confirm_password:
            try:
                register_user(username, full_name, phone_number, email, profession, password)
                st.success("Registration successful! Please log in.")
            except ValueError as e:
                st.error(str(e))
        else:
            st.error("Passwords do not match.")


def admin_login():
    admin_password = st.sidebar.text_input("Enter admin password:", type="password")
    if st.sidebar.button("Login"):
        if admin_password == "admin_password":  # Use a secure password
            st.session_state.admin_authenticated = True
            st.success("Admin logged in successfully.")
        else:
            st.error("Invalid password.")


def admin_dashboard():
    st.header("Admin Dashboard")
    uploaded_files = st.file_uploader("Upload Project Files (TXT/ZIP)", type=["txt", "zip"], accept_multiple_files=True)

    if st.button("Upload Files"):
        if uploaded_files:
            with st.spinner("Processing files..."):
                for uploaded_file in uploaded_files:
                    if uploaded_file.type == "application/zip":
                        process_zip_folder(uploaded_file)
                    else:
                        save_file_to_db(uploaded_file)
                st.success("Files uploaded successfully")
        else:
            st.error("Please upload at least one file.")


if __name__ == "__main__":
    main()
