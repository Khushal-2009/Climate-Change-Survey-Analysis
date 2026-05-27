import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import requests  # Built-in library to send web requests

# Set page configuration
st.set_page_config(page_title="Climate Change Survey & Analysis", layout="wide")

st.title("🌍 Survey on Climate Change")
st.write("Record regional environmental metrics and analyze profiles instantly using public web workflows.")
st.markdown("---")

# =========================================================================
# ⚠️ PASTE YOUR GOOGLE LINKS HERE
# =========================================================================
# 1. Change "/edit..." to "/export?format=csv" at the end of your Google Sheet link so Pandas can read it directly!
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1YsOWWhOpx0fUydBMX4zea63niBOISJBXb97RFvmVXHA/export?format=csv"

# 2. Paste the base URL of your form (remove everything from "/viewform..." onwards)
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1YsOWWhOpx0fUydBMX4zea63niBOISJBXb97RFvmVXHA/edit?gid=0#gid=0/formResponse"

# 3. Paste your exact entry IDs from Step 2
ENTRY_ID_STATE = "entry.518793903"
ENTRY_ID_FACTOR = "entry.543053949"
ENTRY_ID_POINTS = "entry.1820645597"
# =========================================================================

QUESTIONS = {
    "What is the total volume of industrial greenhouse gas emissions?": "Industrial Emissions",
    "What percentage of the state's total electricity is generated from non-renewable sources?": "Non-Renewable Energy",
    "What is the total number of registered fossil-fuel vehicles?": "Fossil-Fuel Vehicles",
    "What percentage of the state's total land area has been deforested?": "Deforestation/Land Conversion",
    "What is the estimated volume of methane emissions produced by agriculture?": "Agricultural Methane",
    "How many incidents of agricultural crop residue burning were recorded?": "Crop Residue Burning",
    "What percentage of municipal solid waste is disposed of in open landfills?": "Unmanaged Landfills"
}

def calculate_percentage_points(value):
    try: return max(0.0, min(100.0, float(value)))
    except ValueError: return 0.0

def calculate_numerical_points(value, min_value, max_value):
    try:
        value = float(value)
        if float(max_value) == float(min_value): return 0.0 
        points = ((value - float(min_value)) / (float(max_value) - float(min_value))) * 100
        return max(0.0, min(100.0, points))
    except ValueError: return 0.0

def submit_to_google_form(state, factor, points):
    """Submits a single row data entry to the Google Sheet via Google Forms."""
    form_data = {
        ENTRY_ID_STATE: state,
        ENTRY_ID_FACTOR: factor,
        ENTRY_ID_POINTS: points
    }
    try:
        # Sends data over standard web protocols
        requests.post(GOOGLE_FORM_URL, data=form_data)
    except Exception as e:
        st.error(f"Failed to submit entry to cloud: {e}")

# --- STREAMLIT UI SECTIONS ---
tab1, tab2 = st.tabs(["📝 Data Entry Form", "📊 Climate Report & Analysis"])

with tab1:
    st.header("Record Climate Metrics")
    states_list = ["Maharashtra", "Tamil Nadu", "Bihar", "Himachal Pradesh"]
    selected_state = st.selectbox("Select the target state:", options=["-- Select a State --"] + states_list, index=0)
    
    if selected_state != "-- Select a State --":
        st.subheader(f"Enter Survey Data for: **{selected_state}**")
        with st.form("survey_form"):
            form_inputs = {}
            count = 0
            for q_text, factor_name in QUESTIONS.items():
                count += 1
                label_suffix = " (Percentage 0-100%)" if count in [2, 4, 7] else " (Enter Raw Value)"
                form_inputs[count] = st.number_input(label=f"Q{count}: {q_text}{label_suffix}", value=0.0, step=1.0, key=f"q_{count}")
            
            submit_button = st.form_submit_button(label="Submit Survey Data")
            if submit_button:
                count = 0
                for q_text, factor_name in QUESTIONS.items():
                    count += 1
                    val = form_inputs[count]
                    if count in [2, 4, 7]:
                        point = calculate_percentage_points(val)
                    else:
                        if count == 1: point = calculate_numerical_points(val, min_value=10, max_value=150)
                        elif count == 3: point = calculate_numerical_points(val, min_value=1500000, max_value=35000000)
                        elif count == 5: point = calculate_numerical_points(val, min_value=100, max_value=800)
                        elif count == 6: point = calculate_numerical_points(val, min_value=50, max_value=4500)
                    
                    # Send each calculated factor row to the form
                    submit_to_google_form(selected_state, QUESTIONS[q_text], round(point, 2))
                
                st.success(f"✅ Data for {selected_state} successfully transmitted to the cloud sheet!")
    else:
        st.info("💡 Please choose a state from the dropdown menu above to start the questionnaire.")

with tab2:
    st.header("Generate Insights & Visualizations")
    
    # Read the data straight from the public Google Sheet link
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
    except Exception:
        df = pd.DataFrame()

    if df.empty or len(df) == 0:
        st.warning("⚠️ No data available yet. Complete a data entry profile in the first tab to begin.")
    else:
        try:
            # Standardize headers case to match Google Form's generated columns
            df.columns = [c.strip().capitalize() for c in df.columns]
            
            if 'State' not in df.columns or 'Factor' not in df.columns or 'Points' not in df.columns:
                st.error("❌ Error: Missing columns. Ensure your Google Form questions are titled exactly: 'State', 'Factor', and 'Points'.")
            else:
                df['Points'] = pd.to_numeric(df['Points'], errors='coerce')
                df = df.dropna(subset=['State', 'Factor', 'Points'])
                df = df.groupby(['State', 'Factor'], as_index=False)['Points'].mean()
                available_states = df['State'].unique().tolist()
                
                analysis_mode = st.selectbox("Analysis Target Mode:", options=["-- Choose Analysis Mode --", "Analyze a Specific State", "Analyze and Compare All States"], index=0)
                selected_states = []
                if analysis_mode == "Analyze a Specific State":
                    state_choice = st.selectbox("Select State for Analysis:", ["-- Choose a State --"] + available_states)
                    if state_choice != "-- Choose a State --": selected_states = [state_choice]
                elif analysis_mode == "Analyze and Compare All States":
                    selected_states = available_states
                
                if selected_states:
                    analysis_df = df[df['State'].isin(selected_states)]
                    st.markdown("---")
                    st.subheader("📝 GENERATED CLIMATE REPORT")
                    
                    for state in selected_states:
                        state_df = analysis_df[analysis_df['State'] == state]
                        st.markdown(f"#### 🌍 State: **{state.upper()}**")
                        high_drivers = state_df[state_df['Points'] >= 70.0]['Factor'].tolist()
                        low_drivers = state_df[state_df['Points'] <= 30.0]['Factor'].tolist()
                        
                        if high_drivers:
                            st.error(f"⚠️ **Critical Drivers of Climate Change:** {', '.join(high_drivers)}")
                            if "Industrial Emissions" in high_drivers or "Fossil-Fuel Vehicles" in high_drivers:
                                st.markdown("<div style='padding:12px; background-color:#e1f5fe; border-left:5px solid #0288d1; border-radius:4px; color:#01579b; margin-bottom:10px;'><strong>💡 Interpretation:</strong> This region shows a strong 'Urban/Industrial Footprint'.</div>", unsafe_allow_html=True)
                            if "Agricultural Methane" in high_drivers or "Crop Residue Burning" in high_drivers:
                                st.markdown("<div style='padding:12px; background-color:#efebe9; border-left:5px solid #5d4037; border-radius:4px; color:#3e2723; margin-bottom:10px;'><strong>💡 Interpretation:</strong> This region shows a prominent 'Rural/Agrarian Footprint'.</div>", unsafe_allow_html=True)
                        else:
                            st.success("✅ **Critical Drivers:** None.")
                        if low_drivers:
                            st.info(f"🌱 **Low Impact Areas:** {', '.join(low_drivers)}")
                    
                    # --- CHARTS ---
                    st.markdown("---")
                    st.subheader("📊 Graphical Profile Plots")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        pivot_df = analysis_df.pivot(index='Factor', columns='State', values='Points')
                        fig_bar, ax_bar = plt.subplots(figsize=(8, 6))
                        pivot_df.plot(kind='bar', width=0.8, ax=ax_bar)
                        ax_bar.set_ylim(0, 110)
                        ax_bar.grid(axis='y', linestyle='--', alpha=0.7)
                        plt.xticks(rotation=45, ha='right')
                        plt.tight_layout()
                        st.pyplot(fig_bar)
                        
                        buffer_bar = io.BytesIO()
                        fig_bar.savefig(buffer_bar, format='png', dpi=300)
                        buffer_bar.seek(0)
                        st.download_button(label="📥 Download Bar Chart", data=buffer_bar, file_name="bar_chart.png", mime="image/png")
                    
                    with col2:
                        factors = df['Factor'].unique().tolist()
                        num_vars = len(factors)
                        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist() + [0]
                        fig_radar, ax_radar = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
                        
                        for state in selected_states:
                            state_df = analysis_df[analysis_df['State'] == state]
                            values = [state_df[state_df['Factor'] == f]['Points'].values[0] if f in state_df['Factor'].values else 0 for f in factors] + [0]
                            ax_radar.plot(angles, values, label=state, linewidth=2)
                            ax_radar.fill(angles, values, alpha=0.15)
                        
                        ax_radar.set_theta_offset(np.pi / 2)
                        ax_radar.set_theta_direction(-1)
                        ax_radar.set_xticks(angles[:-1])
                        ax_radar.set_xticklabels(factors, color='grey', size=9, rotation=45, ha='right')
                        ax_radar.set_ylim(0, 100)
                        plt.tight_layout()
                        st.pyplot(fig_radar)
                        
                        buffer_radar = io.BytesIO()
                        fig_radar.savefig(buffer_radar, format='png', dpi=300)
                        buffer_radar.seek(0)
                        st.download_button(label="📥 Download Radar Chart", data=buffer_radar, file_name="radar_chart.png", mime="image/png")
        except Exception as e:
            st.error(f"Error parsing data: {e}")
