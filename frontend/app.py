"""
HealthIntel — Streamlit Frontend
=================================
AI-Based Medical Report Analysis and Hospital Recommendation System.

Run with: streamlit run frontend/app.py
"""
import streamlit as st
import httpx
import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Page Config ---
st.set_page_config(
    page_title="HealthIntel — AI Medical Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Backend URL ---
BACKEND_URL = os.environ.get("HEALTHINTEL_BACKEND_URL", "http://localhost:8000")

# --- Session State Initialization ---
if "disease_category" not in st.session_state:
    st.session_state.disease_category = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"


def fetch_disease_config():
    """Fetch disease configuration from backend."""
    try:
        resp = httpx.get(f"{BACKEND_URL}/api/disease-config", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    # Fallback: load from local file
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "disease_specialties.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def check_backend():
    """Check if backend is running."""
    try:
        resp = httpx.get(f"{BACKEND_URL}/api/status", timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("## 🏥 HealthIntel")
    st.markdown("---")

    # Navigation
    pages = {
        "home": "🏠 Home",
        "analyze": "🔬 Analyze",
        "hospitals": "🏨 Find Hospitals",
        "about": "ℹ️ About",
    }

    for key, label in pages.items():
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if st.session_state.current_page == key else "secondary"):
            st.session_state.current_page = key
            st.rerun()

    st.markdown("---")

    # Backend status
    backend_up = check_backend()
    if backend_up:
        st.success("✅ Backend Connected")
    else:
        st.error("❌ Backend Offline")
        st.caption(f"Start with:\n`uvicorn backend.main:app --reload`")

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#888; font-size:0.8em;'>"
        "⚠️ Not a medical device.<br>For informational purposes only."
        "</div>",
        unsafe_allow_html=True,
    )


# =============================================================================
# HOME PAGE
# =============================================================================
def render_home():
    st.markdown(
        """
        <div style='text-align:center; padding: 2rem 0;'>
            <h1 style='font-size:2.5rem;'>🏥 HealthIntel</h1>
            <p style='font-size:1.2rem; color:#666; max-width:700px; margin:0 auto;'>
                AI-Based Medical Report Analysis & Hospital Recommendation System
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    disease_config = fetch_disease_config()
    if not disease_config:
        st.warning("Unable to load disease configurations. Please ensure the backend is running.")
        return

    st.markdown("### Select a Disease Category to Begin")
    st.markdown("")

    cols = st.columns(2)
    for i, (key, cfg) in enumerate(disease_config.items()):
        col = cols[i % 2]
        with col:
            available = cfg.get("model_available", cfg.get("available", True))
            icon = cfg.get("icon", "🔬")
            name = cfg.get("display_name", key)
            desc = cfg.get("description", "")
            status = "✅ Available" if available else "⚠️ Not Available"
            status_color = "#22c55e" if available else "#f59e0b"

            st.markdown(
                f"""
                <div style='border:1px solid #ddd; border-radius:12px; padding:1.5rem; margin-bottom:1rem;
                            background: linear-gradient(135deg, #f8f9fa, #ffffff);
                            box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
                    <h3 style='margin:0;'>{icon} {name}</h3>
                    <p style='color:#666; font-size:0.9rem; margin:0.5rem 0;'>{desc}</p>
                    <span style='color:{status_color}; font-size:0.85rem; font-weight:600;'>{status}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if available:
                if st.button(f"Analyze {name}", key=f"select_{key}", use_container_width=True):
                    st.session_state.disease_category = key
                    st.session_state.current_page = "analyze"
                    st.session_state.analysis_result = None
                    st.rerun()
            else:
                st.button(f"{name} (Coming Soon)", key=f"select_{key}", disabled=True, use_container_width=True)

    st.markdown("---")

    # Disclaimer
    st.info(
        "⚠️ **Important Disclaimer**: HealthIntel is an AI-based decision-support tool. "
        "It does NOT provide medical diagnoses or prescriptions. "
        "Always consult qualified healthcare professionals for medical advice."
    )


# =============================================================================
# ANALYZE PAGE
# =============================================================================
def render_analyze():
    disease = st.session_state.disease_category
    if not disease:
        st.warning("Please select a disease category from the Home page.")
        if st.button("← Go to Home"):
            st.session_state.current_page = "home"
            st.rerun()
        return

    disease_config = fetch_disease_config()
    cfg = disease_config.get(disease, {})
    st.markdown(f"## {cfg.get('icon', '🔬')} {cfg.get('display_name', disease)}")
    st.markdown(f"*{cfg.get('description', '')}*")
    st.markdown("---")

    if st.button("← Change Disease Category"):
        st.session_state.disease_category = None
        st.session_state.current_page = "home"
        st.rerun()

    # ----- Heart Failure Form -----
    if disease == "heart_failure":
        st.markdown("### Enter Clinical Parameters")
        with st.form("heart_failure_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                age = st.number_input("Age", min_value=1, max_value=120, value=60)
                anaemia = st.selectbox("Anaemia", [0, 1], format_func=lambda x: "Yes" if x else "No")
                creatinine = st.number_input("Creatinine Phosphokinase (mcg/L)", min_value=1, max_value=10000, value=250)
                diabetes = st.selectbox("Diabetes", [0, 1], format_func=lambda x: "Yes" if x else "No")
            with c2:
                ejection = st.number_input("Ejection Fraction (%)", min_value=1, max_value=100, value=38)
                hbp = st.selectbox("High Blood Pressure", [0, 1], format_func=lambda x: "Yes" if x else "No")
                platelets = st.number_input("Platelets (kiloplatelets/mL)", min_value=1.0, max_value=1000000.0, value=262000.0)
                serum_cr = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, max_value=20.0, value=1.1, step=0.1)
            with c3:
                serum_na = st.number_input("Serum Sodium (mEq/L)", min_value=100, max_value=160, value=137)
                sex = st.selectbox("Sex", [0, 1], format_func=lambda x: "Male" if x else "Female")
                smoking = st.selectbox("Smoking", [0, 1], format_func=lambda x: "Yes" if x else "No")
                time = st.number_input("Follow-up Period (days)", min_value=1, max_value=365, value=115)

            submitted = st.form_submit_button("🔬 Analyze", use_container_width=True, type="primary")

        if submitted:
            payload = {
                "age": age, "anaemia": anaemia, "creatinine_phosphokinase": creatinine,
                "diabetes": diabetes, "ejection_fraction": ejection, "high_blood_pressure": hbp,
                "platelets": platelets, "serum_creatinine": serum_cr, "serum_sodium": serum_na,
                "sex": sex, "smoking": smoking, "time": time,
            }
            with st.spinner("Analyzing..."):
                try:
                    resp = httpx.post(f"{BACKEND_URL}/api/analyze/heart-failure", json=payload, timeout=30)
                    if resp.status_code == 200:
                        st.session_state.analysis_result = resp.json()
                    else:
                        st.error(f"Analysis failed: {resp.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    # ----- Alzheimer Upload -----
    elif disease == "alzheimer":
        st.markdown("### Upload Clinical Data (Excel)")
        st.caption("Upload the Excel file containing Diagnosis, Cognitive Scores, and Brain Measurement data.")
        uploaded = st.file_uploader("Upload .xlsx file", type=["xlsx", "xls"], key="alz_upload")
        if uploaded and st.button("🔬 Analyze", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                try:
                    files = {"file": (uploaded.name, uploaded.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                    resp = httpx.post(f"{BACKEND_URL}/api/analyze/alzheimer", files=files, timeout=60)
                    if resp.status_code == 200:
                        st.session_state.analysis_result = resp.json()
                    else:
                        st.error(f"Analysis failed: {resp.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    # ----- Symptom Prediction -----
    elif disease == "symptom_prediction":
        st.markdown("### Select Your Symptoms")
        try:
            resp = httpx.get(f"{BACKEND_URL}/api/symptoms", timeout=10)
            if resp.status_code == 200:
                symptom_data = resp.json()
                symptom_labels = symptom_data.get("symptoms", [])
                raw_symptoms = symptom_data.get("raw_symptoms", [])

                selected = st.multiselect(
                    "Choose symptoms (select at least 1):",
                    options=raw_symptoms,
                    format_func=lambda x: x.replace("_", " ").title(),
                )

                if selected and st.button("🔬 Analyze", type="primary", use_container_width=True):
                    with st.spinner("Analyzing..."):
                        try:
                            resp2 = httpx.post(
                                f"{BACKEND_URL}/api/analyze/symptoms",
                                json={"symptoms": selected},
                                timeout=30,
                            )
                            if resp2.status_code == 200:
                                st.session_state.analysis_result = resp2.json()
                            else:
                                st.error(f"Analysis failed: {resp2.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Connection error: {e}")
            else:
                st.error("Could not load symptom list from backend.")
        except Exception as e:
            st.error(f"Backend connection error: {e}")

    # ----- Eye Disease (Unavailable) -----
    elif disease == "eye_disease":
        st.warning("⚠️ The Eye Disease Detection module is currently unavailable.")
        st.markdown(
            "The full image dataset is required to train the model. "
            "Please provide the complete Augmented Dataset with all 5 class folders."
        )

    # ----- Display Results -----
    if st.session_state.analysis_result:
        st.markdown("---")
        render_results(st.session_state.analysis_result)


def render_results(result: dict):
    """Render analysis results."""
    st.markdown("## 📊 Analysis Results")

    severity = result.get("severity", {})
    color = severity.get("color", "#6b7280")
    level = severity.get("label", "Unknown")

    # Severity badge
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Prediction", result.get("prediction_label", "N/A"))
    with c2:
        st.metric("Confidence", f"{result.get('confidence', 0)}%")
    with c3:
        st.markdown(
            f"<div style='text-align:center;'>"
            f"<span style='background:{color}; color:white; padding:0.5rem 1rem; "
            f"border-radius:20px; font-weight:600; font-size:1.1rem;'>"
            f"{level}</span></div>",
            unsafe_allow_html=True,
        )

    # Summary
    st.markdown("---")
    st.markdown("### 📋 Health Summary")
    st.markdown(result.get("summary", "No summary available."))

    # Details (expandable)
    details = result.get("details")
    if details:
        with st.expander("🔍 Detailed Results"):
            st.json(details)

    # Disclaimer
    st.markdown("---")
    st.warning(result.get("disclaimer", "This is not a medical diagnosis."))

    # Hospital recommendation button
    if st.button("🏨 Find Nearby Hospitals", type="primary", use_container_width=True):
        st.session_state.current_page = "hospitals"
        st.rerun()


# =============================================================================
# HOSPITAL PAGE
# =============================================================================
def render_hospitals():
    st.markdown("## 🏨 Hospital Recommendations")

    disease = st.session_state.disease_category
    disease_config = fetch_disease_config()
    if disease and disease in disease_config:
        st.info(f"Finding hospitals specializing in: **{disease_config[disease].get('display_name', disease)}**")

    if "map_lat" not in st.session_state:
        st.session_state.map_lat = 28.6139
    if "map_lon" not in st.session_state:
        st.session_state.map_lon = 77.2090

    st.markdown("### 📍 Select Your Location")
    st.caption("Click anywhere on the map to set your current location, or enter the coordinates below.")

    try:
        import folium
        from streamlit_folium import st_folium
        
        m_pick = folium.Map(location=[st.session_state.map_lat, st.session_state.map_lon], zoom_start=5)
        # Allows user to click and see lat/lng, and captures it in Streamlit
        m_pick.add_child(folium.LatLngPopup())
        folium.Marker(
            [st.session_state.map_lat, st.session_state.map_lon], 
            tooltip="Selected Location", 
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m_pick)
        
        map_data = st_folium(m_pick, height=350, width=None, key="location_picker")
        if map_data and map_data.get("last_clicked"):
            new_lat = map_data["last_clicked"]["lat"]
            new_lon = map_data["last_clicked"]["lng"]
            if new_lat != st.session_state.map_lat or new_lon != st.session_state.map_lon:
                st.session_state.map_lat = new_lat
                st.session_state.map_lon = new_lon
                st.rerun()
    except ImportError:
        pass

    c1, c2, c3 = st.columns(3)
    with c1:
        lat = st.number_input("Latitude", value=st.session_state.map_lat, format="%.4f")
    with c2:
        lon = st.number_input("Longitude", value=st.session_state.map_lon, format="%.4f")
    with c3:
        radius = st.slider("Search Radius (km)", 5, 200, 50)
        
    st.session_state.map_lat = lat
    st.session_state.map_lon = lon

    if st.button("🔍 Search Hospitals", type="primary", use_container_width=True):
        with st.spinner("Searching for hospitals..."):
            try:
                payload = {
                    "latitude": lat,
                    "longitude": lon,
                    "disease_category": disease or "heart_failure",
                    "radius_km": radius,
                }
                resp = httpx.post(f"{BACKEND_URL}/api/recommend-hospitals", json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    hospitals = data.get("hospitals", [])
                    st.markdown(f"**Found {data.get('total_found', 0)} hospitals** "
                                f"(Source: {data.get('source', 'unknown')})")

                    if hospitals:
                        # Map
                        try:
                            import folium
                            from streamlit_folium import st_folium

                            m = folium.Map(location=[lat, lon], zoom_start=11)
                            folium.Marker([lat, lon], popup="Your Location",
                                          icon=folium.Icon(color="red", icon="user", prefix="fa")).add_to(m)
                            for h in hospitals:
                                folium.Marker(
                                    [h["latitude"], h["longitude"]],
                                    popup=f"<b>{h['name']}</b><br>{h.get('address', '')}<br>{h.get('distance_km', '?')} km",
                                    icon=folium.Icon(color="blue", icon="plus-sign"),
                                ).add_to(m)
                            st_folium(m, width=None, height=400)
                        except ImportError:
                            st.info("Install `folium` and `streamlit-folium` for map visualization.")

                        # Hospital cards
                        for h in hospitals:
                            with st.container():
                                st.markdown(
                                    f"""
                                    <div style='border:1px solid #ddd; border-radius:10px; padding:1rem; margin:0.5rem 0;
                                                background:#fafafa;'>
                                        <h4 style='margin:0;'>🏥 {h['name']}</h4>
                                        <p style='color:#666; margin:0.3rem 0;'>📍 {h.get('address', 'N/A')}
                                        &nbsp;&nbsp;|&nbsp;&nbsp; 📏 {h.get('distance_km', '?')} km away</p>
                                        <p style='margin:0.2rem 0;'>
                                            {"📞 " + h['phone'] if h.get('phone') else ""}
                                            {"&nbsp;&nbsp;|&nbsp;&nbsp;⭐ " + str(h['rating']) if h.get('rating') else ""}
                                        </p>
                                        <p style='font-size:0.85rem; color:#888;'>
                                            Specialties: {', '.join(h.get('specialties', ['General']))}
                                        </p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.warning("No hospitals found in the specified radius. Try increasing the search radius.")
                else:
                    st.error(f"Error: {resp.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {e}")


# =============================================================================
# ABOUT PAGE
# =============================================================================
def render_about():
    st.markdown(
        """
        ## ℹ️ About HealthIntel

        **HealthIntel** is an AI-based healthcare decision-support system that analyzes
        medical reports and imaging data to assist users in making informed healthcare decisions.

        ### 🎯 Features
        - **Disease-Specific Analysis**: Pre-trained ML models for multiple disease categories
        - **Severity Assessment**: Automated severity level estimation
        - **Health Summaries**: Patient-friendly analysis summaries
        - **Hospital Recommendations**: Nearby hospital finder using OpenStreetMap

        ### 🧪 Available Disease Modules
        | Module | Model | Status |
        |--------|-------|--------|
        | Alzheimer's Detection | Random Forest | ✅ Available |
        | Heart Failure Prediction | Logistic Regression | ✅ Available |
        | Symptom-Based Prediction | Ensemble (RF, XGBoost, CatBoost, LGBM) | ✅ Available |
        | Eye Disease Detection | ResNet34 (fastai) | ⚠️ Dataset Required |

        ### 🛡️ Ethical & Safety Considerations
        - This system does **NOT** provide medical diagnoses or prescriptions
        - Clear disclaimers are shown on all analysis pages
        - Sensitive user data is **NOT** permanently stored
        - Users are encouraged to consult healthcare professionals

        ### 🔧 Technology Stack
        - **Backend**: FastAPI (Python)
        - **Frontend**: Streamlit
        - **ML**: scikit-learn, XGBoost, CatBoost, LightGBM
        - **Hospital Data**: OpenStreetMap Overpass API (free, no API key required)
        - **Mapping**: Folium + Nominatim (free geocoding)

        ---
        *Built as an academic project demonstrating practical AI application in healthcare.*
        """
    )


# =============================================================================
# MAIN ROUTER
# =============================================================================
page_map = {
    "home": render_home,
    "analyze": render_analyze,
    "hospitals": render_hospitals,
    "about": render_about,
}

current = st.session_state.current_page
if current in page_map:
    page_map[current]()
else:
    render_home()
