import csv 
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as pd_st 
import streamlit as st

st.set_page_config(page_title="Climate Change Survey & Analysis", layout="wide")

st.title("🌍 Survey on Climate Change")
st.write("Record regional environmental metrics and analyze aggregated climate profiles.")
st.markdown("---")

FILENAME = "climate_data_csv.csv"

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
    try:
        return max(0.0, min(100.0, float(value)))
    except ValueError:
        return 0.0

def calculate_numerical_points(value, min_value, max_value):
    try:
        value = float(value)
        min_value = float(min_value)
        max_value = float(max_value)
        if max_value == min_value:
            return 0.0 
        points = ((value - min_value) / (max_value - min_value)) * 100
        return max(0.0, min(100.0, points))
    except ValueError:
        return 0.0

def append_to_climate_csv(state_name, factor_name, score_points, filename=FILENAME):
    file_has_content = os.path.exists(filename) and os.path.getsize(filename) > 0
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_has_content:
            writer.writerow(['State', 'Factor', 'Points'])
        writer.writerow([state_name, factor_name, round(score_points, 2)])

tab1, tab2 = st.tabs(["📝 Data Entry Form", "📊 Climate Report & Analysis"])

with tab1:
    st.header("Step 1: Record Climate Metrics")
    
    states_list = ["Maharashtra", "Tamil Nadu", "Bihar", "Himachal Pradesh"]

    selected_state = st.selectbox(
        "Select the target state:", 
        options=["-- Select a State --"] + states_list,
        index=0
    )
    
    if selected_state != "-- Select a State --":
        st.subheader(f"Enter Survey Data for: **{selected_state}**")

        with st.form("survey_form"):
            form_inputs = {}
            count = 0
            
            for q_text, factor_name in QUESTIONS.items():
                count += 1

                if count in [2, 4, 7]:
                    label_suffix = " (Percentage 0-100%)"
                elif count == 1:
                    label_suffix = " (Expected Range: 10 to 150)"
                elif count == 3:
                    label_suffix = " (Expected Range: 1,500,000 to 35,000,000)"
                elif count == 5:
                    label_suffix = " (Expected Range: 100 to 800)"
                elif count == 6:
                    label_suffix = " (Expected Range: 50 to 4,500)"

                form_inputs[count] = st.number_input(
                    label=f"Q{count}: {q_text}{label_suffix}", 
                    value=0.0, 
                    step=1.0,
                    key=f"q_{count}"
                )
            
            submit_button = st.form_submit_button(label="Submit Survey Data")
            
            if submit_button:

                count = 0
                for q_text, factor_name in QUESTIONS.items():
                    count += 1
                    val = form_inputs[count]
                    
                    if count in [2, 4, 7]:
                        point = calculate_percentage_points(val)
                    else:
                        if count == 1:
                            point = calculate_numerical_points(val, min_value=10, max_value=150)
                        elif count == 3:
                            point = calculate_numerical_points(val, min_value=1500000, max_value=35000000)
                        elif count == 5:
                            point = calculate_numerical_points(val, min_value=100, max_value=800)
                        elif count == 6:
                            point = calculate_numerical_points(val, min_value=50, max_value=4500)
                    
                    append_to_climate_csv(selected_state, QUESTIONS[q_text], point)
                
                st.success(f"✅ Data for {selected_state} successfully saved to file!")
    else:
        st.info("💡 Please choose a state from the dropdown menu above to start the questionnaire.")

with tab2:
    st.header("Step 2: Generate Insights & Visualizations")
    
    if not os.path.exists(FILENAME) or os.path.getsize(FILENAME) == 0:
        st.warning("⚠️ No data available yet. Complete a data entry profile in the first tab to begin.")
    else:
        try:
            df = pd.read_csv(FILENAME)
            
            if 'State' not in df.columns or 'Factor' not in df.columns:
                st.error("❌ Error: The CSV file headers are missing or broken. Please clear your file history or fix the columns.")
            else:

                df = df.groupby(['State', 'Factor'], as_index=False)['Points'].mean()
                available_states = df['State'].unique().tolist()
                
                if not available_states:
                    st.error("❌ Error: The CSV file contains no data values.")
                else:

                    analysis_mode = st.radio(
                        "Analysis Target Mode:",
                        options=["-- Choose Analysis Mode --", "Analyze a Specific State", "Analyze and Compare All States"],
                        index=0
                    )
                    
                    selected_states = []
                    if analysis_mode == "Analyze a Specific State":
                        state_choice = st.selectbox("Select State for Analysis:", ["-- Choose a State --"] + available_states)
                        if state_choice != "-- Choose a State --":
                            selected_states = [state_choice]
                            
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
                                    st.caption("💡 *Interpretation:* This region shows a strong 'Urban/Industrial Footprint'. Climate change factors are heavily tied to commercial modernization, congestion, and energy demand.")
                                if "Agricultural Methane" in high_drivers or "Crop Residue Burning" in high_drivers:
                                    st.caption("💡 *Interpretation:* This region shows a prominent 'Rural/Agrarian Footprint'. Climate pressures stem primarily from traditional agricultural practices and land management.")
                            else:
                                st.success("✅ **Critical Drivers:** None of the individual tracked elements have reached critical thresholds relative to the dataset maxima.")
                                
                            if low_drivers:
                                st.info(f"🌱 **Low Impact/Mitigated Areas:** {', '.join(low_drivers)}")
                            st.markdown(" ")

                        st.markdown("---")
                        st.subheader("📊 Graphical Profile Plots")
                        
                        col1, col2 = st.columns(2)

                        with col1:
                            pivot_df = analysis_df.pivot(index='Factor', columns='State', values='Points')
                            fig_bar, ax_bar = plt.subplots(figsize=(8, 6))
                            pivot_df.plot(kind='bar', width=0.8, ax=ax_bar)
                            ax_bar.set_title("Comparative Breakdown of Climate Factors", fontsize=12, fontweight='bold')
                            ax_bar.set_xlabel("Climate Impact Factors", fontsize=10)
                            ax_bar.set_ylabel("Standardized Score (0 - 100 Points)", fontsize=10)
                            ax_bar.set_ylim(0, 110)
                            plt.xticks(rotation=45, ha='right')
                            ax_bar.grid(axis='y', linestyle='--', alpha=0.7)
                            ax_bar.legend(title="States")
                            plt.tight_layout()
                            st.pyplot(fig_bar)

                        with col2:
                            factors = df['Factor'].unique().tolist()
                            num_vars = len(factors)
                            
                            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
                            angles += angles[:1]
                            
                            fig_radar, ax_radar = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
                            
                            for state in selected_states:
                                state_df = analysis_df[analysis_df['State'] == state]
                                values = [state_df[state_df['Factor'] == f]['Points'].values[0] if f in state_df['Factor'].values else 0 for f in factors]
                                values += values[:1]
                                
                                ax_radar.plot(angles, values, label=state, linewidth=2)
                                ax_radar.fill(angles, values, alpha=0.15)
                                
                            ax_radar.set_theta_offset(np.pi / 2)
                            ax_radar.set_theta_direction(-1)

                            ax_radar.set_xticks(angles[:-1])
                            ax_radar.set_xticklabels(factors, color='grey', size=9, rotation=45, ha='right')
                            
                            ax_radar.set_rlabel_position(0)
                            ax_radar.set_yticks([25, 50, 75, 100])
                            ax_radar.set_yticklabels(["25", "50", "75", "100"], color="grey", size=8)
                            ax_radar.set_ylim(0, 100)
                            
                            ax_radar.set_title("Environmental Impact Profile (Radar Chart)", size=12, weight='bold', position=(0.5, 1.1))
                            ax_radar.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
                            plt.tight_layout()
                            st.pyplot(fig_radar)
                            
                    elif analysis_mode != "-- Choose Analysis Mode --":
                        st.info("ℹ️ Select a valid state parameters to populate comparative graphs.")
                        
        except Exception as e:
            st.error(f"An processing anomaly occurred reading the dataset metrics: {e}")