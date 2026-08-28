import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import joblib
import pandas as pd
import tempfile
import re
import html
import urllib.parse
import json
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET

try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False

# ============================================================
# VOICE MODULE
# ============================================================

try:
    from voice_analyzer import analyze_voice
    VOICE_MODULE_AVAILABLE = True
except Exception as e:
    VOICE_MODULE_AVAILABLE = False
    VOICE_IMPORT_ERROR = str(e)

try:
    from streamlit_geolocation import streamlit_geolocation
    GEOLOCATION_AVAILABLE = True
except Exception:
    GEOLOCATION_AVAILABLE = False
    streamlit_geolocation = None


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

# Trusted contact information used by the no-Twilio SOS flow.
# This project version stores it for the current browser session.
if "user_name" not in st.session_state:
    st.session_state.user_name = "Neha"

if "trusted_name" not in st.session_state:
    st.session_state.trusted_name = ""

if "trusted_phone" not in st.session_state:
    st.session_state.trusted_phone = ""

if "sos_requested" not in st.session_state:
    st.session_state.sos_requested = False


# ============================================================
# NO-TWILIO SOS ALERT HELPER
# ============================================================

def render_sos_alert(user_name, trusted_name, trusted_phone):
    """
    Render a browser-based SOS flow without Twilio.

    The browser asks for the current GPS position, builds a Google Maps
    link and prepares SMS/WhatsApp links. The user still has to press
    Send inside SMS/WhatsApp; the application cannot silently send a
    personal SMS without an SMS provider/device integration.
    """

    clean_phone = re.sub(r"[^0-9]", "", trusted_phone or "")
    safe_user = json.dumps(user_name or "User")
    safe_trusted = json.dumps(trusted_name or "Trusted Person")
    safe_phone = json.dumps(clean_phone)

    components.html(
        f"""
        <div style="
            font-family:Arial,sans-serif;
            background:linear-gradient(135deg,#fff1f5,#f4edff);
            border:1px solid #eadcf5;
            border-radius:20px;
            padding:24px;
            box-shadow:0 10px 30px rgba(90,45,110,.12);
        " >

            <div style="text-align:center;">
                <div style="font-size:46px;">🚨</div>
                <h2 style="margin:4px 0;color:#8e1f55;">SOS ALERT</h2>
                <p style="color:#596078;margin-top:5px;">
                    Current location will be added to your emergency message.
                </p>
            </div>

            <div id="sos-status" style="
                margin-top:16px;padding:14px;border-radius:12px;
                background:#fff7fa;color:#596078;
            ">
                📍 Requesting your current location...
            </div>

            <div id="sos-message-box" style="
                display:none;margin-top:16px;padding:16px;border-radius:12px;
                background:white;border:1px solid #eadcf5;
                white-space:pre-wrap;color:#25263b;line-height:1.5;
            " ></div>

            <div id="sos-actions" style="
                display:none;margin-top:18px;text-align:center;
            ">
                <a id="sms-link" href="#" style="
                    display:inline-block;margin:5px;padding:13px 18px;
                    border-radius:10px;background:#e53935;color:white;
                    text-decoration:none;font-weight:700;
                " >📱 Send SMS</a>

                <a id="whatsapp-link" href="#" target="_blank" style="
                    display:inline-block;margin:5px;padding:13px 18px;
                    border-radius:10px;background:#25D366;color:white;
                    text-decoration:none;font-weight:700;
                " >💬 Send WhatsApp</a>
            </div>

            <div style="
                margin-top:14px;font-size:12px;color:#73758a;text-align:center;
            ">
                The message opens in your SMS/WhatsApp app. Please press
                <b>Send</b> to deliver it to the trusted person.
            </div>
        </div>

        <script>
        (function() {{
            const userName = {safe_user};
            const trustedName = {safe_trusted};
            const phone = {safe_phone};
            const status = document.getElementById('sos-status');
            const box = document.getElementById('sos-message-box');
            const actions = document.getElementById('sos-actions');
            const sms = document.getElementById('sms-link');
            const whatsapp = document.getElementById('whatsapp-link');

            if (!phone) {{
                status.innerHTML =
                    '⚠️ No trusted contact number is configured. ' +
                    'Open <b>Settings</b> and add the trusted person number first.';
                return;
            }}

            if (!navigator.geolocation) {{
                status.innerHTML =
                    '❌ Your browser does not support location access.';
                return;
            }}

            navigator.geolocation.getCurrentPosition(
                function(position) {{
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    const maps = 'https://www.google.com/maps?q=' + lat + ',' + lon;
                    const now = new Date();
                    const time = now.toLocaleTimeString([], {{
                        hour: '2-digit', minute: '2-digit'
                    }});

                    const message =
                        '🚨 WOMEN SAFETY AI – SOS ALERT\n\n' +
                        userName + ' may be in an emergency situation and needs help.\n\n' +
                        '👤 Trusted Person: ' + trustedName + '\n' +
                        '📍 Current Location: ' + maps + '\n' +
                        '⏰ Time: ' + time + '\n\n' +
                        'Please contact her immediately.';

                    const encoded = encodeURIComponent(message);
                    sms.href = 'sms:+' + phone + '?body=' + encoded;
                    whatsapp.href = 'https://wa.me/' + phone + '?text=' + encoded;

                    status.innerHTML =
                        '🟢 <b>Location detected successfully.</b><br>' +
                        'Latitude: ' + lat.toFixed(6) + '<br>' +
                        'Longitude: ' + lon.toFixed(6) + '<br>' +
                        'Accuracy: about ' + Math.round(accuracy) + ' m';

                    box.style.display = 'block';
                    box.innerText = message;
                    actions.style.display = 'block';
                }},
                function(error) {{
                    let text = 'Unable to get your location.';
                    if (error.code === 1) text = 'Location permission was denied. Please allow location access and try SOS again.';
                    if (error.code === 2) text = 'Your location could not be determined. Please check GPS/location services.';
                    if (error.code === 3) text = 'Location request timed out. Please try SOS again.';
                    status.innerHTML = '❌ ' + text;
                }},
                {{ enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }}
            );
        }})();
        </script>
        """,
        height=470,
        scrolling=False
    )


# ============================================================
# IMAGE HELPER
# ============================================================

def image_to_base64(path):

    try:

        with open(path, "rb") as file:

            return base64.b64encode(
                file.read()
            ).decode()

    except FileNotFoundError:

        return ""


def get_base64(path):

    return image_to_base64(path)


hero_image = image_to_base64(
    HERO_IMAGE
)


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

risk_model = None

if os.path.exists(MODEL_PATH):

    try:

        risk_model = joblib.load(
            MODEL_PATH
        )

    except Exception as e:

        risk_model = None

        print(
            "Model loading error:",
            e
        )


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

.voice-card {{
    padding: 25px;
    border-radius: 20px;

    background:
        linear-gradient(
            135deg,
            #f4eaff,
            #fff0f7
        );

    border: 1px solid #eadcf5;

    margin-top: 20px;
}}

.voice-result {{
    padding: 25px;
    border-radius: 18px;
    text-align: center;
}}

.news-card {{
    padding: 20px;
    border-radius: 18px;

    background: rgba(255,255,255,0.75);

    border: 1px solid #eadcf5;

    margin-top: 15px;
}}

</style>
"""
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.image(
        MAIN_LOGO,
        width=75
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

    menu_items = [

        ("🏠", "Home"),

        ("🧠", "AI Risk Prediction"),

        ("🎤", "Voice Safety"),

        ("🎥", "Movement Detection"),

        ("📰", "Safety News"),

        ("🚨", "Emergency Alert"),

        ("📍", "Live Location"),

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

        st.session_state.sos_requested = True
        st.session_state.page = "Emergency Alert"
        st.rerun()


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

                <h2>
                    🤖 Machine Learning Safety Analysis
                </h2>

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

                    st.html(
                        """
                        <div class="risk-high">
                            <h1>🔴 HIGH RISK</h1>
                            <p>The AI model detected a high-risk pattern.</p>
                        </div>
                        """
                    )

                    st.warning(
                        "🚨 Early safety action is recommended."
                    )


                elif prediction == "Medium":

                    st.html(
                        """
                        <div class="risk-medium">
                            <h1>🟡 MEDIUM RISK</h1>
                            <p>The AI model detected a moderate-risk pattern.</p>
                        </div>
                        """
                    )

                    st.info(
                        "⚠️ Continue monitoring the situation."
                    )


                else:

                    st.html(
                        """
                        <div class="risk-low">
                            <h1>🟢 LOW RISK</h1>
                            <p>No high-risk pattern was detected from the provided data.</p>
                        </div>
                        """
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


                st.write(
                    "### AI Analysis"
                )


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
                Record a short voice message and the system
                will convert speech to text and analyze it
                for possible distress or unsafe-situation
                indicators.
            </div>

        </div>
        """
    )


    st.write("")


    if not VOICE_MODULE_AVAILABLE:

        st.error(
            "❌ Voice module could not be loaded."
        )

        st.code(
            VOICE_IMPORT_ERROR
        )

        st.info(
            "Make sure voice_analyzer.py is present "
            "inside D:\\Women_Safety_AI"
        )

    else:

        st.html(
            """
            <div class="voice-card">

                <h2>
                    🎤 AI Voice Analysis
                </h2>

                <p>
                    Speak naturally. The system will listen
                    to the recorded audio and analyze the
                    detected speech for safety-related
                    indicators.
                </p>

            </div>
            """
        )


        st.write("")


        st.info(
            "💡 Example: "
            "\"Someone is following me\" or "
            "\"I am in danger, please help me.\""
        )


        audio = st.audio_input(
            "🎤 Click here and record your voice"
        )


        if audio is not None:

            st.success(
                "🎤 Voice recording captured successfully."
            )


            st.audio(
                audio
            )


            if st.button(
                "🧠 ANALYZE VOICE",
                use_container_width=True
            ):

                temp_path = None


                try:

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".wav"
                    ) as temp_file:

                        temp_file.write(
                            audio.getvalue()
                        )

                        temp_path = temp_file.name


                    with st.spinner(
                        "🎤 Converting speech to text and analyzing..."
                    ):

                        result = analyze_voice(
                            temp_path
                        )


                    if not result["success"]:

                        st.error(
                            "❌ Voice analysis failed."
                        )

                        st.warning(
                            result["error"]
                        )


                    else:

                        st.divider()


                        st.subheader(
                            "📝 Detected Speech"
                        )


                        st.write(
                            result["text"]
                        )


                        st.divider()


                        risk = result["risk"]

                        score = result["score"]


                        st.subheader(
                            "🧠 Voice AI Risk Result"
                        )


                        if risk == "High":

                            st.markdown(
                                f"""
                                <div class="risk-high">

                                    <h1>
                                        🔴 HIGH RISK
                                    </h1>

                                    <h2>
                                        Risk Score:
                                        {score}/100
                                    </h2>

                                    <p>
                                        Possible distress or
                                        unsafe-situation
                                        indicators were detected
                                        in the speech.
                                    </p>

                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                            st.error(
                                "🚨 Early safety attention is recommended."
                            )


                        elif risk == "Medium":

                            st.markdown(
                                f"""
                                <div class="risk-medium">

                                    <h1>
                                        🟡 MEDIUM RISK
                                    </h1>

                                    <h2>
                                        Risk Score:
                                        {score}/100
                                    </h2>

                                    <p>
                                        Some possible distress
                                        indicators were detected.
                                    </p>

                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                            st.warning(
                                "⚠️ Continue monitoring the situation."
                            )


                        else:

                            st.markdown(
                                f"""
                                <div class="risk-low">

                                    <h1>
                                        🟢 LOW RISK
                                    </h1>

                                    <h2>
                                        Risk Score:
                                        {score}/100
                                    </h2>

                                    <p>
                                        No strong predefined
                                        distress indicators
                                        were detected.
                                    </p>

                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                        st.write("")


                        st.subheader(
                            "🔎 Detected Safety Indicators"
                        )


                        if result.get(
                            "high_matches"
                        ):

                            st.write(
                                "**High-risk indicators:**"
                            )

                            for word in result[
                                "high_matches"
                            ]:

                                st.write(
                                    f"🔴 {word}"
                                )


                        if result.get(
                            "medium_matches"
                        ):

                            st.write(
                                "**Medium-risk indicators:**"
                            )

                            for word in result[
                                "medium_matches"
                            ]:

                                st.write(
                                    f"🟡 {word}"
                                )


                        if (
                            not result.get(
                                "high_matches"
                            )
                            and
                            not result.get(
                                "medium_matches"
                            )
                        ):

                            st.success(
                                "No predefined distress indicators detected."
                            )


                        st.caption(
                            "⚠️ This is an early-warning prototype. "
                            "A voice signal alone cannot reliably determine "
                            "whether a specific crime will occur."
                        )


                except Exception as e:

                    st.error(
                        "Voice processing error:"
                    )

                    st.code(
                        str(e)
                    )


                finally:

                    if (
                        temp_path
                        and
                        os.path.exists(temp_path)
                    ):

                        os.remove(
                            temp_path
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
                Upload a CCTV or security video and the system will
                analyze frame-to-frame movement to identify unusual
                motion levels and provide an early-warning risk score.
            </div>
        </div>
        """
    )

    st.write("")

    if not CV2_AVAILABLE:
        st.error("❌ OpenCV is not installed.")
        st.info("Run this in PowerShell: pip install opencv-python")
    else:

        st.html(
            """
            <div class="voice-card">
                <h2>🎥 CCTV Video Analysis</h2>
                <p>
                    Upload a short CCTV/security video. The AI prototype
                    compares consecutive video frames and measures how
                    much movement is present.
                </p>
            </div>
            """
        )

        st.write("")

        video_file = st.file_uploader(
            "📁 Upload CCTV / security video",
            type=["mp4", "avi", "mov", "mkv", "webm"],
            help="For faster analysis, use a short video of around 10–30 seconds."
        )

        if video_file is not None:

            st.success("✅ Video uploaded successfully.")

            # Save the uploaded video temporarily so OpenCV can read it.
            temp_video_path = None

            try:
                suffix = os.path.splitext(video_file.name)[1] or ".mp4"

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp_video:

                    temp_video.write(video_file.getbuffer())
                    temp_video_path = temp_video.name

                st.video(video_file)

                st.write("")

                settings_col1, settings_col2 = st.columns(2)

                with settings_col1:
                    sample_every = st.slider(
                        "🎞️ Analyze every Nth frame",
                        min_value=1,
                        max_value=10,
                        value=3,
                        help="Higher values make analysis faster."
                    )

                with settings_col2:
                    motion_threshold = st.slider(
                        "📊 Motion sensitivity",
                        min_value=1,
                        max_value=30,
                        value=8,
                        help="Lower values detect smaller movements."
                    )

                if st.button(
                    "🔍  ANALYZE VIDEO MOVEMENT",
                    use_container_width=True
                ):

                    cap = cv2.VideoCapture(temp_video_path)

                    if not cap.isOpened():
                        st.error(
                            "❌ The video could not be opened. "
                            "Please try an MP4 video."
                        )
                    else:

                        total_frames = int(
                            cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        )
                        fps = cap.get(cv2.CAP_PROP_FPS)

                        if not fps or fps <= 0:
                            fps = 25.0

                        duration = (
                            total_frames / fps
                            if total_frames > 0
                            else 0
                        )

                        previous_gray = None
                        motion_values = []
                        frames_checked = 0
                        frame_number = 0

                        progress = st.progress(0)
                        status = st.empty()

                        while True:

                            ret, frame = cap.read()

                            if not ret:
                                break

                            frame_number += 1

                            if frame_number % sample_every != 0:
                                continue

                            # Resize for faster processing.
                            frame = cv2.resize(
                                frame,
                                (640, 360)
                            )

                            gray = cv2.cvtColor(
                                frame,
                                cv2.COLOR_BGR2GRAY
                            )

                            gray = cv2.GaussianBlur(
                                gray,
                                (21, 21),
                                0
                            )

                            if previous_gray is not None:

                                diff = cv2.absdiff(
                                    previous_gray,
                                    gray
                                )

                                _, thresh = cv2.threshold(
                                    diff,
                                    motion_threshold,
                                    255,
                                    cv2.THRESH_BINARY
                                )

                                # Percentage of the frame containing
                                # noticeable motion.
                                motion_pixels = (
                                    cv2.countNonZero(thresh)
                                    / thresh.size
                                ) * 100

                                motion_values.append(
                                    motion_pixels
                                )

                            previous_gray = gray
                            frames_checked += 1

                            if total_frames > 0:
                                progress.progress(
                                    min(
                                        frame_number / total_frames,
                                        1.0
                                    )
                                )

                            if frames_checked % 10 == 0:
                                status.text(
                                    f"Analyzing video... "
                                    f"{frames_checked} samples checked"
                                )

                        cap.release()
                        progress.progress(1.0)
                        status.empty()

                        if not motion_values:
                            st.warning(
                                "⚠️ Not enough video frames were available "
                                "for movement analysis."
                            )
                        else:

                            average_motion = sum(
                                motion_values
                            ) / len(motion_values)

                            peak_motion = max(
                                motion_values
                            )

                            # Prototype movement-risk scoring.
                            # This measures motion intensity only; it does
                            # not determine whether a crime has occurred.
                            if average_motion >= 8:
                                movement_level = "High"
                                movement_score = min(
                                    100,
                                    round(
                                        average_motion * 5
                                    )
                                )
                            elif average_motion >= 3:
                                movement_level = "Medium"
                                movement_score = min(
                                    100,
                                    round(
                                        average_motion * 8
                                    )
                                )
                            else:
                                movement_level = "Low"
                                movement_score = min(
                                    100,
                                    round(
                                        average_motion * 12
                                    )
                                )

                            st.divider()

                            st.subheader(
                                "🔮 Movement Analysis Result"
                            )

                            if movement_level == "High":

                                st.html(
                                    f"""
                                    <div class="risk-high">
                                        <h1>🔴 HIGH MOVEMENT</h1>
                                        <h2>
                                            Movement Score:
                                            {movement_score}/100
                                        </h2>
                                        <p>
                                            Significant frame-to-frame
                                            movement was detected in the
                                            uploaded video.
                                        </p>
                                    </div>
                                    """
                                )

                                st.warning(
                                    "🚨 High movement detected. "
                                    "Review the CCTV footage carefully."
                                )

                            elif movement_level == "Medium":

                                st.html(
                                    f"""
                                    <div class="risk-medium">
                                        <h1>🟡 MEDIUM MOVEMENT</h1>
                                        <h2>
                                            Movement Score:
                                            {movement_score}/100
                                        </h2>
                                        <p>
                                            Noticeable movement was detected
                                            in the uploaded video.
                                        </p>
                                    </div>
                                    """
                                )

                                st.info(
                                    "⚠️ Moderate movement detected. "
                                    "Continue monitoring the situation."
                                )

                            else:

                                st.html(
                                    f"""
                                    <div class="risk-low">
                                        <h1>🟢 LOW MOVEMENT</h1>
                                        <h2>
                                            Movement Score:
                                            {movement_score}/100
                                        </h2>
                                        <p>
                                            Only limited frame-to-frame
                                            movement was detected.
                                        </p>
                                    </div>
                                    """
                                )

                                st.success(
                                    "✅ Low movement detected in the "
                                    "analyzed video."
                                )

                            st.write("")

                            metric1, metric2, metric3 = st.columns(3)

                            with metric1:
                                st.metric(
                                    "Movement Level",
                                    movement_level
                                )

                            with metric2:
                                st.metric(
                                    "Average Motion",
                                    f"{average_motion:.2f}%"
                                )

                            with metric3:
                                st.metric(
                                    "Peak Motion",
                                    f"{peak_motion:.2f}%"
                                )

                            st.subheader(
                                "📊 Movement Intensity"
                            )

                            motion_df = pd.DataFrame(
                                {
                                    "Sample": range(
                                        1,
                                        len(motion_values) + 1
                                    ),
                                    "Motion (%)": [
                                        round(value, 2)
                                        for value in motion_values
                                    ]
                                }
                            )

                            st.line_chart(
                                motion_df.set_index("Sample")
                            )

                            st.subheader(
                                "📋 Video Information"
                            )

                            info1, info2, info3 = st.columns(3)

                            with info1:
                                st.metric(
                                    "Duration",
                                    f"{duration:.1f} sec"
                                )

                            with info2:
                                st.metric(
                                    "FPS",
                                    f"{fps:.1f}"
                                )

                            with info3:
                                st.metric(
                                    "Frames Analyzed",
                                    frames_checked
                                )

                            st.info(
                                "ℹ️ This is an early-warning movement "
                                "prototype. Motion intensity alone cannot "
                                "reliably determine whether violence, "
                                "harassment, or a crime is occurring. "
                                "The next phase can add person detection, "
                                "pose estimation and behavior analysis."
                            )

            except Exception as e:

                st.error(
                    "❌ Movement analysis error:"
                )

                st.code(
                    str(e)
                )

            finally:

                if (
                    temp_video_path
                    and os.path.exists(temp_video_path)
                ):
                    os.remove(temp_video_path)

        else:

            st.info(
                "🎥 Upload a CCTV/security video above to start "
                "AI movement analysis."
            )

            st.html(
                """
                <div class="ai-card">
                    <h3>🤖 Planned AI Pipeline</h3>
                    <p>
                        CCTV / Video → Person Detection →
                        Pose / Movement Detection →
                        Behavior Analysis → Risk Score →
                        Early Warning
                    </p>
                </div>
                """
            )

            st.caption(
                "Supported formats: MP4, AVI, MOV, MKV and WEBM. "
                "Short videos are recommended for faster analysis."
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
                Get recent public-safety and women's-safety news,
                automatically collect articles, classify their safety
                relevance, and explore the latest stories.
            </div>
        </div>
        """
    )

    st.write("")

    # ------------------------------------------------------------
    # NEWS HELPERS
    # ------------------------------------------------------------

    def clean_news_text(value):
        value = html.unescape(value or "")
        value = re.sub(r"<[^>]+>", " ", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    def fetch_google_news_rss(query, limit=30):
        """
        Fetch public Google News RSS results for a safety-related query.
        This is intentionally lightweight and does not require an API key.
        """
        encoded_query = urllib.parse.quote_plus(query)

        url = (
            "https://news.google.com/rss/search?"
            f"q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/151.0 Safari/537.36"
                )
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=12
        ) as response:

            xml_data = response.read()

        root = ET.fromstring(xml_data)

        articles = []

        for item in root.findall("./channel/item")[:limit]:

            title = clean_news_text(
                item.findtext("title", "")
            )

            description = clean_news_text(
                item.findtext("description", "")
            )

            link = (
                item.findtext("link", "")
                or ""
            ).strip()

            pub_date = (
                item.findtext("pubDate", "")
                or ""
            ).strip()

            source_node = item.find("source")

            source_name = ""

            if source_node is not None:
                source_name = (
                    source_node.text or ""
                ).strip()

            if title and link:
                articles.append(
                    {
                        "title": title,
                        "description": description,
                        "link": link,
                        "published": pub_date,
                        "source": source_name or "News source",
                    }
                )

        return articles

    def classify_safety_news(article):
        """
        Simple NLP-style keyword classifier for the first working version.
        It can later be replaced with a trained NLP model.
        """

        text = (
            article["title"]
            + " "
            + article["description"]
        ).lower()

        categories = {
            "Women's Safety": [
                "women",
                "woman",
                "girl",
                "girls",
                "female",
                "women safety",
                "women's safety",
                "harassment",
                "stalking",
                "eve teasing",
                "sexual harassment",
                "domestic violence",
            ],
            "Crime & Violence": [
                "crime",
                "criminal",
                "murder",
                "assault",
                "attack",
                "violence",
                "rape",
                "kidnap",
                "kidnapping",
                "robbery",
                "molestation",
                "abuse",
            ],
            "Public Safety": [
                "public safety",
                "safety",
                "police",
                "emergency",
                "accident",
                "road safety",
                "security",
                "missing",
                "rescue",
                "disaster",
            ],
        }

        scores = {
            category: sum(
                1
                for keyword in keywords
                if keyword in text
            )
            for category, keywords in categories.items()
        }

        best_category = max(
            scores,
            key=scores.get
        )

        best_score = scores[best_category]

        if best_score >= 3:
            relevance = "High"
        elif best_score >= 1:
            relevance = "Medium"
        else:
            relevance = "General"

        return best_category, relevance

    def collect_safety_news():
        """
        Collect up to 150 unique articles from several public RSS searches.
        """
        queries = [
            "women safety India",
            "women crime India",
            "women harassment India",
            "public safety India",
            "crime safety India",
            "police emergency India",
        ]

        all_articles = []
        seen = set()

        for query in queries:

            try:

                results = fetch_google_news_rss(
                    query,
                    limit=30
                )

                for article in results:

                    key = (
                        article["title"]
                        .lower()
                        .strip()
                    )

                    if key in seen:
                        continue

                    seen.add(key)

                    category, relevance = (
                        classify_safety_news(
                            article
                        )
                    )

                    article["category"] = category
                    article["relevance"] = relevance

                    all_articles.append(
                        article
                    )

                    if len(all_articles) >= 150:
                        return all_articles

            except Exception:
                # Continue with the other queries if one source/search fails.
                continue

        return all_articles

    # ------------------------------------------------------------
    # NEWS CONTROLS
    # ------------------------------------------------------------

    control1, control2, control3 = st.columns(
        [2, 2, 1]
    )

    with control1:

        news_category = st.selectbox(
            "🗂️ Category",
            [
                "All",
                "Women's Safety",
                "Crime & Violence",
                "Public Safety",
            ]
        )

    with control2:

        news_relevance = st.selectbox(
            "🎯 Relevance",
            [
                "All",
                "High",
                "Medium",
                "General",
            ]
        )

    with control3:

        st.write("")
        refresh_news = st.button(
            "🔄 Refresh News",
            use_container_width=True
        )

    if (
        "safety_news_articles"
        not in st.session_state
    ):
        st.session_state.safety_news_articles = []

    if refresh_news:

        st.session_state.safety_news_articles = []

    if not st.session_state.safety_news_articles:

        st.info(
            "📰 Click **Load Latest Safety News** to collect "
            "recent safety-related articles."
        )

        if st.button(
            "📰  LOAD LATEST SAFETY NEWS",
            use_container_width=True
        ):

            with st.spinner(
                "Collecting recent safety news..."
            ):

                articles = (
                    collect_safety_news()
                )

            if articles:

                st.session_state.safety_news_articles = (
                    articles
                )

                st.success(
                    f"✅ Collected {len(articles)} "
                    "unique safety-related articles."
                )

                st.rerun()

            else:

                st.error(
                    "❌ No news could be collected right now. "
                    "Please check your internet connection and try again."
                )

    else:

        articles = (
            st.session_state.safety_news_articles
        )

        filtered_articles = [

            article

            for article in articles

            if (
                news_category == "All"
                or article["category"] == news_category
            )

            and (
                news_relevance == "All"
                or article["relevance"] == news_relevance
            )

        ]

        # --------------------------------------------------------
        # SUMMARY
        # --------------------------------------------------------

        st.html(
            f"""
            <div class="ai-card">
                <h2>🤖 AI News Analysis</h2>
                <p>
                    The system collected
                    <strong>{len(articles)}</strong>
                    unique articles and classified them
                    using safety-related text keywords.
                </p>
            </div>
            """
        )

        st.write("")

        high_count = sum(
            1
            for article in articles
            if article["relevance"] == "High"
        )

        medium_count = sum(
            1
            for article in articles
            if article["relevance"] == "Medium"
        )

        women_count = sum(
            1
            for article in articles
            if article["category"] == "Women's Safety"
        )

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric(
                "📰 Total Articles",
                len(articles)
            )

        with m2:
            st.metric(
                "🔴 High Relevance",
                high_count
            )

        with m3:
            st.metric(
                "🟡 Medium Relevance",
                medium_count
            )

        with m4:
            st.metric(
                "👩 Women's Safety",
                women_count
            )

        st.write("")

        st.subheader(
            f"📰 Latest Safety News ({len(filtered_articles)})"
        )

        if not filtered_articles:

            st.warning(
                "No articles match the selected filters."
            )

        else:

            for index, article in enumerate(
                filtered_articles
            ):

                if article["relevance"] == "High":

                    badge = "🔴 HIGH"

                elif article["relevance"] == "Medium":

                    badge = "🟡 MEDIUM"

                else:

                    badge = "🟢 GENERAL"

                title = html.escape(
                    article["title"]
                )

                source = html.escape(
                    article["source"]
                )

                category = html.escape(
                    article["category"]
                )

                published = html.escape(
                    article["published"]
                )

                description = html.escape(
                    article["description"]
                )

                if len(description) > 300:
                    description = (
                        description[:300]
                        + "..."
                    )

                st.html(
                    f"""
                    <div class="page-card"
                         style="margin-top:14px;">

                        <div style="
                            font-size:20px;
                            font-weight:800;
                            color:{TEXT};
                            line-height:1.35;
                        ">
                            {title}
                        </div>

                        <div style="
                            margin-top:9px;
                            color:{MUTED};
                            font-size:14px;
                        ">
                            {badge}
                            &nbsp; • &nbsp;
                            {category}
                            &nbsp; • &nbsp;
                            {source}
                        </div>

                        <div style="
                            margin-top:8px;
                            color:{MUTED};
                            font-size:13px;
                        ">
                            🕒 {published}
                        </div>

                        <div style="
                            margin-top:10px;
                            color:{TEXT};
                            line-height:1.55;
                        ">
                            {description}
                        </div>

                    </div>
                    """
                )

                st.link_button(
                    "🔗 Read Full Article",
                    article["link"],
                    use_container_width=True
                )

        st.write("")

        st.info(
            "ℹ️ News classification is a prototype based on "
            "safety-related keywords. It does not verify the truth "
            "or severity of an article. Always open the original "
            "source before making decisions."
        )

        st.caption(
            "Data source: public Google News RSS search results. "
            "The application does not store or publish the articles."
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
            use_container_width=True,
            key="emergency_sos_button"
        ):

            st.session_state.sos_requested = True
            st.rerun()

    if st.session_state.get("sos_requested", False):

        st.divider()
        st.subheader("🚨 Emergency Message Center")

        trusted_name = st.session_state.get("trusted_name", "")
        trusted_phone = st.session_state.get("trusted_phone", "")

        if not trusted_phone:
            st.warning(
                "⚠️ No trusted contact is configured yet. "
                "Go to **Settings** and save a trusted person's name and mobile number."
            )
        else:
            st.info(
                f"📱 Alert prepared for **{trusted_name or 'Trusted Person'}** "
                f"({trusted_phone})."
            )

            render_sos_alert(
                st.session_state.get("user_name", "User"),
                trusted_name,
                trusted_phone
            )

        if st.button("✖️ Close SOS Panel", key="close_sos_panel"):
            st.session_state.sos_requested = False
            st.rerun()


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
                Get your current browser location, view it on a map,
                and quickly open or share the location when help is needed.
            </div>
        </div>
        """
    )

    st.write("")

    if not GEOLOCATION_AVAILABLE:

        st.error("❌ Browser location module is not installed.")

        st.info(
            "Run this in PowerShell: "
            "pip install streamlit-geolocation"
        )

        st.markdown(
            "After installation, restart Streamlit and open the "
            "**📍 Live Location** page again."
        )

    else:

        st.html(
            """
            <div class="ai-card">
                <h2>📍 Location Safety Center</h2>
                <p>
                    Click <b>Get My Current Location</b> and allow your
                    browser to share your location. Your coordinates will
                    then be displayed on the map below.
                </p>
            </div>
            """
        )

        st.write("")

        # Browser geolocation component.
        location = streamlit_geolocation()

        if location:

            # The streamlit-geolocation component normally returns
            # latitude/longitude directly. The fallback handling below
            # also supports a nested coords object.
            if isinstance(location, dict) and "error" in location:

                error = location.get("error", {})
                error_message = (
                    error.get("message", "Location could not be obtained.")
                    if isinstance(error, dict)
                    else str(error)
                )

                st.error(
                    f"❌ Location error: {error_message}"
                )

            else:

                if isinstance(location, dict):

                    coords = location.get(
                        "coords",
                        location
                    )

                    latitude = coords.get(
                        "latitude"
                    )

                    longitude = coords.get(
                        "longitude"
                    )

                    accuracy = coords.get(
                        "accuracy"
                    )

                    altitude = coords.get(
                        "altitude"
                    )

                    speed = coords.get(
                        "speed"
                    )

                else:

                    latitude = None
                    longitude = None
                    accuracy = None
                    altitude = None
                    speed = None

                if (
                    latitude is not None
                    and longitude is not None
                ):

                    try:
                        latitude = float(latitude)
                        longitude = float(longitude)
                    except Exception:
                        latitude = None
                        longitude = None

                if (
                    latitude is not None
                    and longitude is not None
                ):

                    st.session_state["current_latitude"] = latitude
                    st.session_state["current_longitude"] = longitude
                    st.session_state["current_accuracy"] = accuracy
                    st.session_state["current_altitude"] = altitude
                    st.session_state["current_speed"] = speed

        # Use the latest successful location stored in this session.
        latitude = st.session_state.get(
            "current_latitude"
        )

        longitude = st.session_state.get(
            "current_longitude"
        )

        accuracy = st.session_state.get(
            "current_accuracy"
        )

        altitude = st.session_state.get(
            "current_altitude"
        )

        speed = st.session_state.get(
            "current_speed"
        )

        if (
            latitude is not None
            and longitude is not None
        ):

            st.success(
                "🟢 Location received successfully."
            )

            st.write("")

            # -------------------------------
            # MAP
            # -------------------------------

            st.html(
                """
                <div class="page-card">
                    <div class="page-title">
                        🗺️ Your Current Location
                    </div>
                    <div class="page-description">
                        The marker below represents the latest location
                        received from your browser.
                    </div>
                </div>
                """
            )

            map_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport"
                      content="width=device-width, initial-scale=1.0">

                <link
                    rel="stylesheet"
                    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
                >

                <style>
                    html, body {{
                        margin: 0;
                        padding: 0;
                        width: 100%;
                        height: 100%;
                        overflow: hidden;
                        font-family: Arial, sans-serif;
                    }}

                    #map {{
                        width: 100%;
                        height: 430px;
                        border-radius: 18px;
                    }}
                </style>
            </head>

            <body>

                <div id="map"></div>

                <script
                    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">
                </script>

                <script>
                    const latitude = {latitude};
                    const longitude = {longitude};

                    const map = L.map("map").setView(
                        [latitude, longitude],
                        16
                    );

                    L.tileLayer(
                        "https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",
                        {{
                            maxZoom: 19,
                            attribution:
                                '&copy; OpenStreetMap contributors'
                        }}
                    ).addTo(map);

                    const marker = L.marker(
                        [latitude, longitude]
                    ).addTo(map);

                    marker.bindPopup(
                        "<b>📍 Your Current Location</b><br>" +
                        "Latitude: " + latitude.toFixed(6) + "<br>" +
                        "Longitude: " + longitude.toFixed(6)
                    ).openPopup();

                    L.circle(
                        [latitude, longitude],
                        {{
                            radius: 100,
                            color: "#e91e63",
                            fillColor: "#e91e63",
                            fillOpacity: 0.12
                        }}
                    ).addTo(map);
                </script>

            </body>
            </html>
            """

            components.html(
                map_html,
                height=450,
                scrolling=False
            )

            st.write("")

            # -------------------------------
            # LOCATION DETAILS
            # -------------------------------

            st.subheader(
                "📌 Location Details"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Latitude",
                    f"{latitude:.6f}"
                )

            with col2:
                st.metric(
                    "Longitude",
                    f"{longitude:.6f}"
                )

            with col3:

                if accuracy is not None:

                    try:
                        accuracy_text = (
                            f"{float(accuracy):.1f} m"
                        )
                    except Exception:
                        accuracy_text = str(accuracy)

                else:
                    accuracy_text = "N/A"

                st.metric(
                    "Accuracy",
                    accuracy_text
                )

            extra1, extra2, extra3 = st.columns(3)

            with extra1:

                if altitude is not None:

                    try:
                        altitude_text = (
                            f"{float(altitude):.1f} m"
                        )
                    except Exception:
                        altitude_text = str(altitude)

                else:
                    altitude_text = "N/A"

                st.metric(
                    "Altitude",
                    altitude_text
                )

            with extra2:

                if speed is not None:

                    try:
                        speed_text = (
                            f"{float(speed):.2f} m/s"
                        )
                    except Exception:
                        speed_text = str(speed)

                else:
                    speed_text = "N/A"

                st.metric(
                    "Movement Speed",
                    speed_text
                )

            with extra3:

                st.metric(
                    "Status",
                    "ACTIVE"
                )

            st.write("")

            # -------------------------------
            # OPEN / SHARE
            # -------------------------------

            maps_url = (
                "https://www.google.com/maps/search/?api=1"
                f"&query={latitude},{longitude}"
            )

            st.subheader(
                "📤 Location Actions"
            )

            action1, action2 = st.columns(2)

            with action1:

                st.link_button(
                    "🗺️ OPEN IN GOOGLE MAPS",
                    maps_url,
                    use_container_width=True
                )

            with action2:

                if st.button(
                    "📋 COPY LOCATION",
                    use_container_width=True,
                    key="copy_location_button"
                ):

                    st.code(
                        f"{latitude:.6f}, {longitude:.6f}"
                    )

                    st.success(
                        "Location coordinates displayed. "
                        "You can copy them from the box above."
                    )

            st.write("")

            st.html(
                f"""
                <div class="risk-medium">
                    <h2>🚨 Emergency Location Sharing</h2>
                    <p>
                        If an emergency occurs, this location can be
                        included in your emergency message.
                    </p>
                    <p>
                        <b>Current coordinates:</b>
                        {latitude:.6f}, {longitude:.6f}
                    </p>
                </div>
                """
            )

            st.info(
                "🔐 Privacy: location is requested by your browser and "
                "is shown in this session. The application does not "
                "automatically send your coordinates to an emergency "
                "contact."
            )

        else:

            st.info(
                "📍 No location has been received yet. "
                "Click the location button above and allow your browser "
                "to access your location."
            )

            st.html(
                """
                <div class="ai-card">
                    <h3>🛡️ How Live Location Works</h3>
                    <p>
                        1. Click <b>Get My Current Location</b>.
                    </p>
                    <p>
                        2. Allow location access in your browser.
                    </p>
                    <p>
                        3. Your coordinates appear on the map.
                    </p>
                    <p>
                        4. Open the location in Google Maps or use it
                        when reporting an emergency.
                    </p>
                </div>
                """
            )

            st.warning(
                "⚠️ If your browser asks for permission, choose "
                "'Allow'. Location access may not work if permission "
                "has been blocked in browser settings."
            )


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
        "For a real deployment, configure these numbers "
        "according to the country/region where the "
        "application will be used."
    )


    contacts = [

        (
            "🚨 Emergency Services",
            "112"
        ),

        (
            "👮 Police",
            "100"
        ),

        (
            "🚑 Ambulance",
            "108"
        ),

        (
            "🚒 Fire Services",
            "101"
        )

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
                Voice and AI-based detection will gradually
                reduce the need for manual reporting.
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
                Your safety assistant can provide guidance
                and safety information.
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
                "AI assistant functionality can be "
                "connected to your NLP/AI model here."
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

    # ------------------------------------------------------------
    # TRUSTED CONTACT
    # ------------------------------------------------------------

    st.subheader("👤 Profile & Trusted Person")

    user_name_input = st.text_input(
        "👩 Your Name",
        value=st.session_state.get("user_name", "Neha"),
        placeholder="Example: Neha"
    )

    st.session_state.user_name = user_name_input.strip() or "User"

    st.info(
        "Add a trusted family member or friend. This number is used "
        "to prepare the SOS SMS/WhatsApp message. No Twilio account is required."
    )

    contact_col1, contact_col2 = st.columns(2)

    with contact_col1:
        trusted_name_input = st.text_input(
            "👤 Trusted Person Name",
            value=st.session_state.get("trusted_name", ""),
            placeholder="Example: Mother"
        )

    with contact_col2:
        trusted_phone_input = st.text_input(
            "📱 Trusted Person Mobile Number",
            value=st.session_state.get("trusted_phone", ""),
            placeholder="Example: +919876543210"
        )

    if st.button(
        "💾 SAVE TRUSTED CONTACT",
        use_container_width=True,
        key="save_trusted_contact"
    ):
        cleaned_phone = re.sub(r"[^0-9+]", "", trusted_phone_input.strip())

        if not trusted_name_input.strip():
            st.warning("Please enter the trusted person's name.")
        elif len(re.sub(r"[^0-9]", "", cleaned_phone)) < 10:
            st.warning("Please enter a valid mobile number with country code, for example +919876543210.")
        else:
            st.session_state.trusted_name = trusted_name_input.strip()
            st.session_state.trusted_phone = cleaned_phone
            st.success("✅ Trusted contact saved successfully for this session.")

    st.caption(
        "Tip: For India, use international format such as +919876543210. "
        "The browser will open SMS/WhatsApp; you must press Send."
    )

    st.divider()

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