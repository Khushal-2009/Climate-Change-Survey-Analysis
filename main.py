import csv 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
print("\n" + "="*30)
print(" SURVEY ON CLIMATE CHANGE")
print("="*30)

questions= {
    "What is the total volume of industrial greenhouse gas emissions?": "Industrial Emissions",
    "What percentage of the state's total electricity is generated from non-renewable sources?": "Non-Renewable Energy",
    "What is the total number of registered fossil-fuel vehicles?": "Fossil-Fuel Vehicles",
    "What percentage of the state's total land area has been deforested?": "Deforestation/Land Conversion",
    "What is the estimated volume of methane emissions produced by agriculture?": "Agricultural Methane",
    "How many incidents of agricultural crop residue burning were recorded?": "Crop Residue Burning",
    "What percentage of municipal solid waste is disposed of in open landfills?": "Unmanaged Landfills"
}

def Ques_Ans():
    l = ["Maharashtra","Tamil Nadu","Bihar","Himachal Pradesh"]
    for x in l:
        print(x)
    state = input("Enter the state from above:")
    count = 0
    for x in questions:
        print(x)
        count+=1
        if count in [2,4,7]:
            value = float(input("Enter the answer of the above question:"))
            point = calculate_percentage_points(value)
            append_to_climate_csv(state,questions[x],point)
        else:
            value = float(input("Enter the answer of the above question:"))
            if count == 1:
                point = calculate_numerical_points(value,min_value=10,max_value=150)
            elif count == 3:
                point = calculate_numerical_points(value,min_value=1500000,max_value=35000000)
            elif count == 5:
                point = calculate_numerical_points(value,min_value=100,max_value=800)
            elif count == 6:
                point = calculate_numerical_points(value,min_value=50,max_value=4500)

            append_to_climate_csv(state,questions[x],point)

def generate_climate_report_and_plots():
    filename = "climate_data_csv.csv"

    try:
        df = pd.read_csv(filename)

        if 'State' not in df.columns or 'Factor' not in df.columns:
            print("❌ Error: The CSV file headers are missing or broken. Please delete 'climate_data_csv.csv' and re-enter data.")
            return

        df = df.groupby(['State', 'Factor'], as_index=False)['Points'].mean()
        
    except FileNotFoundError:
        print(f"❌ Error: The file '{filename}' was not found. Please run your data collection first.")
        return
    
    available_states = df['State'].unique().tolist()
    if not available_states:
        print("❌ Error: The CSV file is empty.")
        return

    print("\n📊 --- Climate Data Analysis Menu --- 📊")
    print("1. Analyze a Specific State")
    print("2. Analyze and Compare All States")
    choice = input("Enter your choice (1 or 2): ").strip()

    selected_states = []
    if choice == '1':
        print("\nAvailable States:")
        for idx, state in enumerate(available_states, 1):
            print(f"{idx}. {state}")
        try:
            state_idx = int(input("Select a state by entering its number: ")) - 1
            if 0 <= state_idx < len(available_states):
                selected_states = [available_states[state_idx]]
            else:
                print("❌ Invalid selection.")
                return
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            return
    elif choice == '2':
        selected_states = available_states
    else:
        print("❌ Invalid choice. Exiting analysis.")
        return

    analysis_df = df[df['State'].isin(selected_states)]

    print("\n" + "="*50)
    print("📝 GENERATED CLIMATE REPORT")
    print("="*50)
    
    for state in selected_states:
        state_df = analysis_df[analysis_df['State'] == state]
        print(f"\n🌍 State: {state.upper()}")

        high_drivers = state_df[state_df['Points'] >= 70.0]['Factor'].tolist()
        low_drivers = state_df[state_df['Points'] <= 30.0]['Factor'].tolist()
        
        if high_drivers:
            print(f"  ⚠️ Critical Drivers of Climate Change: {', '.join(high_drivers)}")

            if "Industrial Emissions" in high_drivers or "Fossil-Fuel Vehicles" in high_drivers:
                print("  💡 Interpretation: This region shows a strong 'Urban/Industrial Footprint'. Climate change factors are heavily tied to commercial modernization, congestion, and energy demand.")
            if "Agricultural Methane" in high_drivers or "Crop Residue Burning" in high_drivers:
                print("  💡 Interpretation: This region shows a prominent 'Rural/Agrarian Footprint'. Climate pressures stem primarily from traditional agricultural practices and land management.")
        else:
            print("  ✅ Critical Drivers: None of the individual tracked elements have reached critical thresholds relative to the dataset maxima.")
            
        if low_drivers:
            print(f"  🌱 Low Impact/Mitigated Areas: {', '.join(low_drivers)}")
            
    print("\nGenerating charts... (Close the chart windows to finish)")


    pivot_df = analysis_df.pivot(index='Factor', columns='State', values='Points')
    
    plt.figure(figsize=(10, 6))
    pivot_df.plot(kind='bar', width=0.8, ax=plt.gca())
    plt.title("Comparative Breakdown of Climate Change Factors", fontsize=14, fontweight='bold')
    plt.xlabel("Climate Impact Factors", fontsize=12)
    plt.ylabel("Standardized Score (0 - 100 Points)", fontsize=12)
    plt.ylim(0, 110)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title="States")
    plt.tight_layout()
    

    factors = df['Factor'].unique().tolist()
    num_vars = len(factors)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1] 
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    for state in selected_states:
        state_df = analysis_df[analysis_df['State'] == state]

        values = [state_df[state_df['Factor'] == f]['Points'].values[0] if f in state_df['Factor'].values else 0 for f in factors]
        values += values[:1] 
        
        ax.plot(angles, values, label=state, linewidth=2)
        ax.fill(angles, values, alpha=0.15)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], factors, color='grey', size=10, rotation=90)

    ax.set_rlabel_position(0)
    plt.yticks([25, 50, 75, 100], ["25", "50", "75", "100"], color="grey", size=8)
    plt.ylim(0, 100)
    
    plt.title("Environmental Impact Profile (Radar Chart)", size=14, weight='bold', position=(0.5, 1.1))
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1))
    plt.tight_layout()

    plt.show()


def append_to_climate_csv(state_name, factor_name, score_points, filename="climate_data_csv.csv"):

    file_has_content = os.path.exists(filename) and os.path.getsize(filename) > 0

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        if not file_has_content:
            writer.writerow(['State', 'Factor', 'Points'])

        writer.writerow([state_name, factor_name, round(score_points, 2)])

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

Ques_Ans()
generate_climate_report_and_plots()
