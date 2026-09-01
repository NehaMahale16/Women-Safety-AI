import streamlit as st
import base64
import os
import joblib
import pandas as pd
from datetime import datetime, timedelta

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Women Safety AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# FILE PATHS
# ============================================================

HERO_IMAGE = "static/women.png"
MAIN_LOGO = "static/logos/main_logo.png"
EMERGENCY_LOGO = "static/logos/emergency_logo.png"
APP_ICON = "static/logos/app_icon.png"

MODEL_PATH = "models/risk_prediction_model.pkl"


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "notification" not in st.session_state:
    st.session_state.notification = False

if "safety_timer_end" not in st.session_state:
    st.session_state.safety_timer_end = None

if "safety_timer_expired" not in st.session_state:
    st.session_state.safety_timer_expired = False


# ============================================================
# IMAGE HELPER
# ============================================================

def image_to_base64(path):

    try:
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()

    except FileNotFoundError:
        return ""


# FIX FOR OLD get_base64 ERROR
def get_base64(path):
    return image_to_base64(path)


hero_image = image_to_base64(HERO_IMAGE)


# ============================================================
# LOAD ML MODEL
# ============================================================

risk_model = None

if os.path.exists(MODEL_PATH):

    try:
        risk_model = joblib.load(MODEL_PATH)

    except Exception as e:
        risk_model = None
        print("Model loading error:", e)


# ============================================================
# THEME
# ============================================================

if st.session_state.dark_mode:

    BG = "#120d20"
    CARD = "rgba(35, 25, 55, 0.90)"
    TEXT = "#ffffff"
    MUTED = "#d0c8dc"

else:

    BG = "#fff8fc"
    CARD = "rgba(255, 255, 255, 0.88)"
    TEXT = "#111638"
    MUTED = "#596078"


# ============================================================
# GLOBAL CSS
# ============================================================

st.html(
    f"""
<style>

.stApp {{
    background: {BG};
}}

.main .block-container {{
    padding-top: 0.8rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    padding-bottom: 1rem;
    max-width: 100%;
}}


[data-testid="stSidebar"] {{
    min-width: 325px;
    max-width: 325px;

    background:
        linear-gradient(
            180deg,
            #fff8fc 0%,
            #f6efff 50%,
            #ffffff 100%
        );

    border-right: 1px solid #eee0f5;
}}


[data-testid="stSidebar"] > div:first-child {{
    padding-top: 1.2rem;
    padding-left: 1rem;
    padding-right: 1rem;
}}


.brand-area {{
    padding: 8px 4px 14px 4px;
}}

.brand-title {{
    color: #111638;
    font-size: 25px;
    font-weight: 800;
    line-height: 1.1;
    margin-top: 5px;
}}

.brand-subtitle {{
    color: #353657;
    font-size: 15px;
    margin-top: 8px;
}}


.menu-heading {{
    color: #17183d;
    font-size: 18px;
    font-weight: 800;
    margin-top: 15px;
    margin-bottom: 8px;
}}


.hero {{
    position: relative;
    width: 100%;
    min-height: 760px;
    border-radius: 0;
    overflow: hidden;

    background-image:
        url("data:image/png;base64,{hero_image}");

    background-size: cover;
    background-position: center;

    box-shadow:
        0 8px 35px rgba(70, 30, 90, 0.12);
}}


.hero::after {{
    content: "";

    position: absolute;
    inset: 0;

    background:
        linear-gradient(
            90deg,
            rgba(255, 245, 250, 0.94) 0%,
            rgba(255, 245, 250, 0.82) 37%,
            rgba(255, 235, 245, 0.34) 70%,
            rgba(255, 220, 235, 0.08) 100%
        );
}}


.hero-content {{
    position: relative;
    z-index: 2;
    width: 64%;
    padding-top: 105px;
    padding-left: 70px;
}}


.hero-badge {{
    display: inline-block;

    padding: 10px 18px;
    border-radius: 30px;

    background:
        linear-gradient(
            90deg,
            rgba(232, 194, 255, 0.78),
            rgba(255, 208, 238, 0.78)
        );

    border: 1px solid rgba(210, 120, 235, 0.25);

    color: #9a35b6;

    font-size: 17px;
    font-weight: 700;

    margin-bottom: 22px;
}}


.hero-title {{
    color: #111638;

    font-size: 66px;
    line-height: 1.03;
    font-weight: 850;

    margin: 0;

    letter-spacing: -2px;
}}


.hero-gradient-title {{
    margin-top: 16px;

    font-size: 35px;
    line-height: 1.15;
    font-weight: 800;

    background:
        linear-gradient(
            90deg,
            #6547c7,
            #e344a9
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}


.hero-description {{
    color: #4d526c;

    font-size: 19px;
    line-height: 1.55;

    max-width: 700px;

    margin-top: 22px;
    margin-bottom: 28px;
}}


.feature-row {{
    display: flex;
    gap: 18px;
    max-width: 750px;
}}


.feature-card {{
    flex: 1;

    min-height: 150px;

    padding: 22px 18px;

    background:
        rgba(255, 255, 255, 0.82);

    border:
        1px solid
        rgba(255, 255, 255, 0.90);

    border-radius: 17px;

    box-shadow:
        0 10px 30px
        rgba(90, 45, 110, 0.12);

    backdrop-filter: blur(8px);

    text-align: center;
}}


.feature-icon {{
    width: 52px;
    height: 52px;

    margin: auto;

    display: flex;

    align-items: center;
    justify-content: center;

    border-radius: 50%;

    font-size: 27px;

    background:
        linear-gradient(
            135deg,
            #ffe6f3,
            #eee3ff
        );
}}


.feature-title {{
    color: #18183d;

    font-size: 17px;
    font-weight: 800;

    margin-top: 10px;
}}


.feature-text {{
    color: #596078;

    font-size: 13px;
    line-height: 1.35;

    margin-top: 5px;
}}


.quote-box {{
    max-width: 750px;

    margin-top: 28px;

    padding: 22px 30px;

    border-radius: 17px;

    background:
        linear-gradient(
            90deg,
            rgba(55, 39, 117, 0.97),
            rgba(47, 40, 108, 0.94)
        );

    color: white;

    box-shadow:
        0 12px 30px
        rgba(40, 25, 90, 0.25);

    display: flex;

    align-items: center;

    gap: 18px;
}}


.quote-icon {{
    width: 52px;
    height: 52px;

    flex-shrink: 0;

    border-radius: 50%;

    border: 2px solid #e678ce;

    display: flex;

    align-items: center;
    justify-content: center;

    font-size: 28px;

    color: #ff87dc;
}}


.quote-main {{
    font-size: 19px;
    font-weight: 500;
}}


.quote-small {{
    font-size: 21px;
    font-style: italic;

    color: #ff87dc;

    margin-top: 5px;
}}


.quote-heart {{
    margin-left: auto;

    color: #ff6bc8;

    font-size: 30px;
}}


.emergency-sidebar {{
    background:
        linear-gradient(
            135deg,
            #f8d7ee,
            #f0d5fa
        );

    border-radius: 16px;

    padding: 20px;

    margin-top: 25px;
}}


.emergency-sidebar-title {{
    color: #4c255d;

    font-size: 18px;
    font-weight: 800;
}}


.emergency-sidebar-text {{
    color: #67516e;

    font-size: 13px;

    margin-top: 5px;
    margin-bottom: 14px;
}}


.page-card {{
    background: {CARD};

    border-radius: 20px;

    padding: 35px;

    box-shadow:
        0 8px 30px
        rgba(80, 40, 100, 0.10);
}}


.page-title {{
    color: {TEXT};

    font-size: 40px;

    font-weight: 800;
}}


.page-description {{
    color: {MUTED};

    font-size: 17px;

    line-height: 1.6;
}}


.ai-card {{
    padding: 25px;

    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            rgba(240, 225, 255, 0.95),
            rgba(255, 235, 247, 0.95)
        );

    box-shadow:
        0 10px 30px
        rgba(90, 45, 110, 0.12);

    margin-top: 20px;
}}


.risk-high {{
    padding: 25px;

    border-radius: 18px;

    background: #ffe2e2;

    border: 2px solid #ff7070;

    text-align: center;
}}


.risk-medium {{
    padding: 25px;

    border-radius: 18px;

    background: #fff4cf;

    border: 2px solid #e5bd36;

    text-align: center;
}}


.risk-low {{
    padding: 25px;

    border-radius: 18px;

    background: #ddf7e5;

    border: 2px solid #53b86b;

    text-align: center;
}}

</style>
"""
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # Sidebar image restored - uses the same women.png image
    # that is already used as the dashboard hero image.
    st.image(
        HERO_IMAGE,
        width=80
    )

    st.html(
        """
        <div class="brand-area">

            <div class="brand-title">
                Women Safety AI
            </div>

            <div class="brand-subtitle">
                Your Safety, Our Priority
            </div>

        </div>
        """
    )


    st.html(
        """
        <div class="menu-heading">
            MENU
        </div>
        """
    )


    # NEW AI FEATURES ADDED HERE
    menu_items = [

        ("🏠", "Home"),

        ("🧠", "AI Risk Prediction"),

        ("🎤", "Voice Safety"),

        ("🎥", "Movement Detection"),

        ("📰", "Safety News"),

        ("🚨", "Emergency Alert"),

        ("📍", "Live Location"),
        ("⏱️", "Safety Timer"),

        ("🛡️", "Safety Tips"),

        ("📞", "Helpline Numbers"),

        ("📋", "Report Incident"),

        ("🤖", "AI Assistant"),

        ("ⓘ", "About Us")

    ]


    for icon, name in menu_items:

        if st.button(
            f"{icon}   {name}",
            key=f"menu_{name}",
            use_container_width=True
        ):

            st.session_state.page = name

            st.rerun()


    st.html(
        """
        <div class="emergency-sidebar">

            <div class="emergency-sidebar-title">
                📞 &nbsp; In Emergency?
            </div>

            <div class="emergency-sidebar-text">
                Help is just one click away.
            </div>

        </div>
        """
    )


    if st.button(
        "🚨  SEND SOS ALERT",
        key="sidebar_sos",
        use_container_width=True
    ):

        st.error(
            "🚨 SOS ALERT ACTIVATED"
        )

        st.warning(
            "Please contact the appropriate local emergency service or a trusted person immediately."
        )


# ============================================================
# TOP BAR
# ============================================================

top1, top2, top3, top4 = st.columns(
    [6, 1, 1, 1]
)


with top2:

    if st.button(
        "🔔 Notifications",
        use_container_width=True
    ):

        st.session_state.notification = True


with top3:

    if st.button(
        "⚙️ Settings",
        use_container_width=True
    ):

        st.session_state.page = "Settings"

        st.rerun()


with top4:

    if st.button(
        "🌙 Dark Mode",
        use_container_width=True
    ):

        st.session_state.dark_mode = not st.session_state.dark_mode

        st.rerun()


if st.session_state.notification:

    st.info(
        "🔔 You have no new safety notifications."
    )


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "Home":

    st.html(
        f"""
        <div class="hero">

            <div class="hero-content">

                <div class="hero-badge">
                    🛡️ &nbsp; Empower • Protect • Support
                </div>

                <div class="hero-title">
                    Women Safety AI
                </div>

                <div class="hero-gradient-title">
                    Smart Protection, Anytime, Anywhere.
                </div>

                <div class="hero-description">

                    Your safety matters. Our AI-powered system
                    is here to support, protect and empower you
                    in every situation.

                </div>


                <div class="feature-row">


                    <div class="feature-card">

                        <div class="feature-icon">
                            🚨
                        </div>

                        <div class="feature-title">
                            Quick Alert
                        </div>

                        <div class="feature-text">
                            Send SOS alert in emergencies
                        </div>

                    </div>


                    <div class="feature-card">

                        <div class="feature-icon">
                            📍
                        </div>

                        <div class="feature-title">
                            Live Tracking
                        </div>

                        <div class="feature-text">
                            Share your live location instantly
                        </div>

                    </div>


                    <div class="feature-card">

                        <div class="feature-icon">
                            🧠
                        </div>

                        <div class="feature-title">
                            AI Prediction
                        </div>

                        <div class="feature-text">
                            Analyze safety risk using AI
                        </div>

                    </div>


                    <div class="feature-card">

                        <div class="feature-icon">
                            📞
                        </div>

                        <div class="feature-title">
                            24/7 Support
                        </div>

                        <div class="feature-text">
                            Access important helpline numbers
                        </div>

                    </div>


                </div>


                <div class="quote-box">

                    <div class="quote-icon">
                        “
                    </div>

                    <div>

                        <div class="quote-main">
                            You are Strong. You are Brave. You are Safe.
                        </div>

                        <div class="quote-small">
                            We are with you, always.
                        </div>

                    </div>

                    <div class="quote-heart">
                        ♡
                    </div>

                </div>


            </div>

        </div>
        """
    )


# ============================================================
# AI RISK PREDICTION
# ============================================================

elif st.session_state.page == "AI Risk Prediction":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                🧠 AI Risk Prediction
            </div>

            <div class="page-description">

                Our Machine Learning model analyzes
                safety-related information and predicts
                the current safety risk.

            </div>

        </div>
        """
    )


    if risk_model is None:

        st.error(
            "❌ Risk prediction model not found."
        )

        st.info(
            "Make sure this file exists: "
            "models/risk_prediction_model.pkl"
        )

    else:

        st.html(
            """
            <div class="ai-card">

                <h2>🤖 Machine Learning Safety Analysis</h2>

                <p>
                Enter the current situation below.
                The Random Forest model will estimate
                the safety risk.
                </p>

            </div>
            """
        )


        st.write("")


        col1, col2 = st.columns(2)


        with col1:

            device = st.selectbox(
                "📱 Device Type",
                [
                    "Smartphone",
                    "Smartwatch",
                    "Panic Button Device"
                ]
            )


            panic = st.selectbox(
                "🚨 Panic Button Activation",
                [
                    "Yes",
                    "No"
                ]
            )


            response_time = st.number_input(
                "⏱️ Response Time (minutes)",
                min_value=1,
                max_value=60,
                value=10
            )


            day = st.selectbox(
                "📅 Day",
                [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday"
                ]
            )


        with col2:

            location = st.selectbox(
                "📍 Location Type",
                [
                    "Street",
                    "Public Transport",
                    "Shopping Area",
                    "Residential Area",
                    "Workplace",
                    "Other"
                ]
            )


            age = st.number_input(
                "👤 Age",
                min_value=10,
                max_value=100,
                value=22
            )


            emergency_contact = st.selectbox(
                "📞 Emergency Contact Status",
                [
                    "Notified with Confirmation",
                    "Notified with Delay",
                    "Not Notified"
                ]
            )


        st.write("")


        if st.button(
            "🔍  ANALYZE SAFETY RISK",
            use_container_width=True
        ):

            input_data = pd.DataFrame(
                [
                    {
                        "Device Type": device,

                        "Panic Button Activation": panic,

                        "Response Time (minutes)": response_time,

                        "Day": day,

                        "Location Type": location,

                        "Age": age,

                        "Emergency Contact Status":
                            emergency_contact
                    }
                ]
            )


            try:

                prediction = risk_model.predict(
                    input_data
                )[0]


                probabilities = risk_model.predict_proba(
                    input_data
                )[0]


                classes = risk_model.classes_


                max_probability = max(
                    probabilities
                )


                st.divider()


                st.subheader(
                    "🔮 AI Prediction Result"
                )


                if prediction == "High":

                    st.markdown(
                        """
                        <div class="risk-high">

                            <h1>🔴 HIGH RISK</h1>

                            <p>
                            The AI model detected a
                            high-risk pattern.
                            </p>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    st.warning(
                        "🚨 Early safety action is recommended."
                    )


                elif prediction == "Medium":

                    st.markdown(
                        """
                        <div class="risk-medium">

                            <h1>🟡 MEDIUM RISK</h1>

                            <p>
                            The AI model detected a
                            moderate-risk pattern.
                            </p>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    st.info(
                        "⚠️ Continue monitoring the situation."
                    )


                else:

                    st.markdown(
                        """
                        <div class="risk-low">

                            <h1>🟢 LOW RISK</h1>

                            <p>
                            No high-risk pattern was
                            detected from the provided data.
                            </p>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                st.write("")


                col1, col2, col3 = st.columns(3)


                with col1:

                    st.metric(
                        "Predicted Risk",
                        prediction
                    )


                with col2:

                    st.metric(
                        "AI Confidence",
                        f"{max_probability * 100:.2f}%"
                    )


                with col3:

                    st.metric(
                        "Model",
                        "Random Forest"
                    )


                st.subheader(
                    "📊 Risk Probability"
                )


                probability_data = pd.DataFrame(
                    {
                        "Risk Level": classes,
                        "Probability": [
                            round(
                                p * 100,
                                2
                            )
                            for p in probabilities
                        ]
                    }
                )


                st.bar_chart(
                    probability_data.set_index(
                        "Risk Level"
                    )
                )


                st.write("### AI Analysis")


                st.write(
                    f"""
                    **Predicted Risk:** {prediction}

                    **AI Confidence:** {max_probability * 100:.2f}%

                    **Model:** Random Forest Classifier

                    **Input Factors:** Device type,
                    panic button status, response time,
                    day, location type, age and emergency
                    contact status.
                    """
                )


            except Exception as e:

                st.error(
                    "Prediction error:"
                )

                st.code(
                    str(e)
                )


# ============================================================
# VOICE SAFETY
# ============================================================

elif st.session_state.page == "Voice Safety":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                🎤 Voice Safety Detection
            </div>

            <div class="page-description">

                This module will analyze voice/audio
                for possible distress signals and
                unsafe speech patterns.

            </div>

        </div>
        """
    )


    st.write("")


    st.info(
        "🎤 Voice AI module will be connected in the next development phase."
    )


    st.write(
        "Planned pipeline:"
    )


    st.code(
        """
Microphone
    ↓
Speech Recognition
    ↓
Speech-to-Text
    ↓
NLP Analysis
    ↓
Distress Detection
    ↓
Risk Score
    ↓
Emergency Warning
        """
    )


# ============================================================
# MOVEMENT DETECTION
# ============================================================

elif st.session_state.page == "Movement Detection":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                🎥 AI Movement Detection
            </div>

            <div class="page-description">

                CCTV/video analysis will detect
                unusual movement and potentially
                dangerous behavioral patterns.

            </div>

        </div>
        """
    )


    st.write("")


    st.info(
        "🎥 CCTV movement detection will be connected in the next development phase."
    )


    st.code(
        """
CCTV / Video
      ↓
Person Detection
      ↓
Pose / Movement Detection
      ↓
Behavior Analysis
      ↓
AI Risk Model
      ↓
Early Warning
        """
    )


# ============================================================
# SAFETY NEWS
# ============================================================

elif st.session_state.page == "Safety News":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                📰 Safety News
            </div>

            <div class="page-description">

                News related to women's safety,
                crime awareness and public safety
                will be collected and analyzed here.

            </div>

        </div>
        """
    )


    st.write("")


    st.info(
        "📰 News dataset and web-scraping module will be connected in the next development phase."
    )


    st.code(
        """
Public News Sources
        ↓
Web Scraper
        ↓
100–200 News Articles
        ↓
Text Cleaning
        ↓
NLP Analysis
        ↓
Safety Categories
        """
    )


# ============================================================
# EMERGENCY ALERT
# ============================================================

elif st.session_state.page == "Emergency Alert":

    emergency_image = get_base64(
        EMERGENCY_LOGO
    )


    st.html(
        f"""
        <div class="page-card">

            <div style="
                text-align:center;
                padding:20px;
            ">

                <img
                    src="data:image/png;base64,{emergency_image}"
                    width="220"
                >

                <div class="page-title">
                    🚨 Emergency Alert
                </div>

                <div class="page-description">

                    Use the emergency alert when you are
                    in immediate danger or need urgent help.

                </div>

            </div>

        </div>
        """
    )


    st.write("")


    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )


    with col2:

        if st.button(
            "🚨  SEND SOS ALERT",
            use_container_width=True
        ):

            st.error(
                "🚨 SOS ALERT ACTIVATED"
            )

            st.warning(
                "Please contact the appropriate local emergency service or a trusted person immediately."
            )


# ============================================================
# LIVE LOCATION
# ============================================================

elif st.session_state.page == "Live Location":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                📍 Live Location
            </div>

            <div class="page-description">

                This section can be connected to
                location/GPS functionality.

            </div>

        </div>
        """
    )


    st.write("")


    st.info(
        "📍 Location sharing functionality can be added here."
    )


# ============================================================
# SAFETY TIMER
# ============================================================

elif st.session_state.page == "Safety Timer":

    st.html(
        """
        <div class="page-card">
            <div class="page-title">
                ⏱️ Safety Timer
            </div>
            <div class="page-description">
                Start a safety countdown before travelling.
                When the timer finishes, the app will ask if you are safe.
            </div>
        </div>
        """
    )

    st.write("")

    # Start a new timer
    if st.session_state.safety_timer_end is None:
        st.info("💡 Example: Start a 30-minute timer before travelling home.")

        duration = st.selectbox(
            "⏱️ Select safety timer duration",
            [5, 10, 15, 20, 30, 45, 60],
            index=4,
            format_func=lambda x: f"{x} minutes"
        )

        if st.button("▶️ START SAFETY TIMER", use_container_width=True):
            st.session_state.safety_timer_end = datetime.now() + timedelta(minutes=duration)
            st.session_state.safety_timer_expired = False
            st.rerun()

    else:
        # Refresh the page every second so the countdown stays live.
        if st_autorefresh is not None:
            st_autorefresh(interval=1000, key="safety_timer_refresh")

        remaining_seconds = max(
            0,
            int((st.session_state.safety_timer_end - datetime.now()).total_seconds())
        )

        if remaining_seconds > 0:
            minutes, seconds = divmod(remaining_seconds, 60)

            st.html(
                f"""
                <div class="page-card" style="text-align:center;">
                    <div style="font-size:18px; font-weight:700; color:{MUTED};">
                        🛡️ Your safety timer is active
                    </div>
                    <div style="font-size:64px; font-weight:900; margin:20px 0; color:#5c3aa8;">
                        {minutes:02d}:{seconds:02d}
                    </div>
                    <div style="font-size:16px; color:{MUTED};">
                        Time remaining
                    </div>
                </div>
                """
            )

            if st.button("⏹️ STOP TIMER", use_container_width=True):
                st.session_state.safety_timer_end = None
                st.session_state.safety_timer_expired = False
                st.rerun()

        else:
            st.session_state.safety_timer_expired = True
            st.html(
                """
                <div class="page-card" style="text-align:center; border:2px solid #ff4b4b;">
                    <div style="font-size:42px;">⏰</div>
                    <div class="page-title">Are you safe?</div>
                    <div class="page-description">
                        Your safety timer has finished. Please confirm your status.
                    </div>
                </div>
                """
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🟢 YES, I'M SAFE", use_container_width=True):
                    st.session_state.safety_timer_end = None
                    st.session_state.safety_timer_expired = False
                    st.success("✅ Great! Your safety timer has been completed safely.")
                    st.rerun()

            with col2:
                if st.button("🔴 I NEED HELP", use_container_width=True):
                    st.error("🚨 Emergency help requested.")
                    st.warning(
                        "Use the SOS alert below to notify a trusted person or contact local emergency services."
                    )

            if st.button("🚨 SEND SOS ALERT", use_container_width=True):
                st.error("🚨 SOS ALERT ACTIVATED")
                st.warning(
                    "Please contact the appropriate local emergency service or a trusted person immediately."
                )

            if st.button("🔄 START NEW TIMER", use_container_width=True):
                st.session_state.safety_timer_end = None
                st.session_state.safety_timer_expired = False
                st.rerun()


# ============================================================
# SAFETY TIPS
# ============================================================

elif st.session_state.page == "Safety Tips":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                🛡️ Safety Tips
            </div>

            <div class="page-description">

                Important safety practices for
                everyday situations.

            </div>

        </div>
        """
    )


    tips = [

        (
            "👀 Stay aware of your surroundings",
            "Avoid distractions when walking in unfamiliar areas."
        ),

        (
            "📱 Keep your phone charged",
            "Make sure your phone has enough battery when travelling."
        ),

        (
            "📞 Keep emergency contacts ready",
            "Keep trusted contacts easily accessible."
        ),

        (
            "🚶 Avoid isolated areas",
            "Choose well-lit and populated routes whenever possible."
        ),

        (
            "📍 Share your location",
            "When appropriate, share your location with someone you trust."
        ),

        (
            "🗣️ Trust your instincts",
            "If something feels unsafe, move toward a safer environment."
        )

    ]


    for title, description in tips:

        st.html(
            f"""
            <div class="page-card"
                 style="margin-top:15px;">

                <div style="
                    color:#5c3aa8;
                    font-size:19px;
                    font-weight:800;
                ">

                    {title}

                </div>

                <div style="
                    color:{MUTED};
                    margin-top:7px;
                ">

                    {description}

                </div>

            </div>
            """
        )


# ============================================================
# HELPLINE NUMBERS
# ============================================================

elif st.session_state.page == "Helpline Numbers":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                📞 Helpline Numbers
            </div>

            <div class="page-description">

                Keep important emergency contacts accessible.

            </div>

        </div>
        """
    )


    st.write("")


    st.warning(
        "For a real deployment, configure these numbers according to the country/region where the application will be used."
    )


    contacts = [

        ("🚨 Emergency Services", "112"),

        ("👮 Police", "100"),

        ("🚑 Ambulance", "108"),

        ("🚒 Fire Services", "101")

    ]


    for name, number in contacts:

        col1, col2 = st.columns(
            [3, 1]
        )


        with col1:

            st.write(
                f"**{name}**"
            )


        with col2:

            st.write(
                f"**{number}**"
            )


# ============================================================
# REPORT INCIDENT
# ============================================================

elif st.session_state.page == "Report Incident":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                📋 Report Incident
            </div>

            <div class="page-description">

                Record information about a safety incident.

            </div>

        </div>
        """
    )


    st.write("")


    incident_type = st.selectbox(
        "Incident Type",
        [
            "Select an option",
            "Harassment",
            "Suspicious Activity",
            "Unsafe Location",
            "Other"
        ]
    )


    description = st.text_area(
        "Describe the incident"
    )


    if st.button(
        "📋 Submit Report",
        use_container_width=True
    ):

        if incident_type == "Select an option":

            st.warning(
                "Please select an incident type."
            )

        else:

            st.success(
                "Your incident report has been recorded by the application."
            )


# ============================================================
# AI ASSISTANT
# ============================================================

elif st.session_state.page == "AI Assistant":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                🤖 AI Assistant
            </div>

            <div class="page-description">

                Your safety assistant can provide
                guidance and safety information.

            </div>

        </div>
        """
    )


    st.write("")


    question = st.text_input(
        "How can I help you?"
    )


    if st.button(
        "🤖 Ask AI",
        use_container_width=True
    ):

        if question.strip():

            st.info(
                "AI assistant functionality can be connected to your AI model here."
            )

        else:

            st.warning(
                "Please enter a question."
            )


# ============================================================
# ABOUT US
# ============================================================

elif st.session_state.page == "About Us":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                ⓘ About Women Safety AI
            </div>

            <div class="page-description">

                Women Safety AI is designed to provide
                accessible safety assistance, emergency
                support and useful safety information.

                <br><br>

                Our goal is simple:

                <br><br>

                <b>
                Empower • Protect • Support
                </b>

            </div>

        </div>
        """
    )


# ============================================================
# SETTINGS
# ============================================================

elif st.session_state.page == "Settings":

    st.html(
        """
        <div class="page-card">

            <div class="page-title">
                ⚙️ Settings
            </div>

            <div class="page-description">

                Customize your Women Safety AI dashboard.

            </div>

        </div>
        """
    )


    st.write("")


    dark = st.checkbox(
        "🌙 Dark Mode",
        value=st.session_state.dark_mode
    )


    if dark != st.session_state.dark_mode:

        st.session_state.dark_mode = dark

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.write("")


st.html(
    f"""
    <div style="
        text-align:center;
        color:{MUTED};
        font-size:13px;
        padding:10px;
    ">

        🛡️ Women Safety AI
        &nbsp; • &nbsp;
        Empower • Protect • Support

    </div>
    """
)
