import streamlit as st
from pymongo import MongoClient
import datetime

# -----------------------
# MongoDB Connection
# -----------------------
MONGO_URI = st.secrets["MONGODB_URI"]  # keep your Mongo URI in secrets
client = MongoClient(MONGO_URI)
db = client["trinovous_db"]
users_collection = db["users"]
habits_collection = db["habits"]

# -----------------------
# App Title
# -----------------------
st.set_page_config(page_title="Trinovous AI Companion", layout="wide")
st.title("🌟 Trinovous AI Companion")
st.write("Your personal AI companion that remembers you, tracks your habits, and grows with you!")

# -----------------------
# User Login / Signup
# -----------------------
st.sidebar.header("Login / Signup")

user_email = st.sidebar.text_input("Enter your Email")
user_name = st.sidebar.text_input("Enter your Name")
login_btn = st.sidebar.button("Login / Signup")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if login_btn and user_email:
    user = users_collection.find_one({"email": user_email})
    if not user:
        users_collection.insert_one({"email": user_email, "name": user_name})
        st.sidebar.success(f"Welcome {user_name}! Your account is created.")
    else:
        st.sidebar.success(f"Welcome back {user['name']}!")
    st.session_state.logged_in = True
    st.session_state.user = user_email

# -----------------------
# If logged in
# -----------------------
if st.session_state.logged_in:

    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📋 Habit Tracker", "📊 Dashboard"])

    # -----------------------
    # Chat Tab
    # -----------------------
    with tab1:
        st.subheader("Chat with Trinovous 🤖")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input("You: ", key="chat_input")
        if st.button("Send"):
            if user_input:
                # Simple AI Response (can be replaced with OpenAI / HuggingFace)
                ai_response = f"I remember that you said: '{user_input}'. Interesting!"
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("Trinovous", ai_response))

        for sender, message in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"**🧑 You:** {message}")
            else:
                st.markdown(f"**🤖 Trinovous:** {message}")

    # -----------------------
    # Habit Tracker
    # -----------------------
    with tab2:
        st.subheader("Track Your Habits ✅")

        habit = st.text_input("Enter a habit you practiced today:")
        if st.button("Log Habit"):
            if habit:
                habits_collection.insert_one({
                    "user": st.session_state.user,
                    "habit": habit,
                    "date": datetime.date.today().isoformat()
                })
                st.success("Habit logged successfully!")

        st.write("### Your Habits")
        user_habits = habits_collection.find({"user": st.session_state.user})
        for h in user_habits:
            st.write(f"- {h['habit']} ({h['date']})")

    # -----------------------
    # Dashboard
    # -----------------------
    with tab3:
        st.subheader("Habit Dashboard 📊")

        habits = list(habits_collection.find({"user": st.session_state.user}))
        if habits:
            st.write(f"Total habits logged: **{len(habits)}**")
            dates = [h['date'] for h in habits]
            st.bar_chart(dates)
        else:
            st.info("No habits logged yet. Start adding habits to see your progress!")

else:
    st.info("Please log in using the sidebar to start.")
