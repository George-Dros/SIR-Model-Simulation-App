import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

# SIR model differential equations
def sir_model(S, I, R, beta, gamma, N):
    dS = -beta * S * I / N
    dI = beta * S * I / N - gamma * I
    dR = gamma * I
    return dS, dI, dR

# Simulation function
def run_simulation(N, I0, R0, beta, gamma, days):
    S, I, R = N - I0 - R0, I0, R0
    S_list, I_list, R_list = [S], [I], [R]

    for _ in range(days):
        dS, dI, dR = sir_model(S, I, R, beta, gamma, N)
        S += dS
        I += dI
        R += dR
        S_list.append(S)
        I_list.append(I)
        R_list.append(R)

    return pd.DataFrame({
        'Day': list(range(days + 1)),
        'Susceptible': S_list,
        'Infected': I_list,
        'Recovered': R_list
    })

# Streamlit App
st.title("📊 SIR Epidemic Simulator")
st.markdown("Explore how an infectious disease spreads through a population using the classic SIR model.")

# Sidebar
analysis_mode = st.sidebar.selectbox(
    "Analysis Type",
    ["Single Simulation", "Beta Sensitivity", "Beta–Gamma Heatmap"]
)
N = st.sidebar.slider("Total Population (N)", 100, 1000000, 10000, step=100)
I0 = st.sidebar.slider("Initial Infected (I₀)", 1, N // 10, 10)
R0 = st.sidebar.slider("Initial Recovered (R₀)", 0, N // 10, 0)
beta = st.sidebar.slider("Infection Rate (β)", 0.0, 1.0, 0.3, step=0.01)
gamma = st.sidebar.slider("Recovery Rate (γ)", 0.0, 1.0, 0.1, step=0.01)
days = st.sidebar.slider("Simulation Duration (days)", 10, 365, 160)

if analysis_mode == "Single Simulation":
    # run single simulation
    df = run_simulation(N, I0, R0, beta, gamma, days)

    # Plot
    st.write("### Infection Curve")
    st.line_chart(df.set_index("Day"))

    # Final numbers
    st.write("### Final State")
    st.write(df.iloc[-1])
elif analysis_mode == "Beta Sensitivity":
    beta_values = [beta * (1 + pct) for pct in [-0.2, -0.1, 0, 0.1, 0.2]]

    fig, ax = plt.subplots()
    results = {}
    for b in beta_values:
        df = run_simulation(N, I0, R0, b, gamma, days)
        results[b] = df
        ax.plot(df["Day"], df["Infected"], label=f'β={b:.2f}')

    ax.set_title("Sensitivity Analysis: Infection Curves for Different β")
    ax.set_xlabel("Day")
    ax.set_ylabel("Infected")
    ax.legend()

    st.pyplot(fig)

    st.write("### Final Infected Counts by β")
    for b in beta_values:
        final_infected = df["Infected"].iloc[-1]
        st.write(f"β = {b:.2f} → Infected = {final_infected:,.0f}")
elif analysis_mode == "Beta–Gamma Heatmap":
    st.write("### Heatmap of Peak Infected for β–γ Combinations")
    
    beta_values = np.linspace(0.1, 0.5, 5)    # [0.1, 0.2, 0.3, 0.4, 0.5]
    gamma_values = np.linspace(0.05, 0.25, 5) # [0.05, 0.1, 0.15, 0.2, 0.25]

    heatmap_data = np.zeros((len(beta_values), len(gamma_values)))

    for i, b in enumerate(beta_values):
        for j, g in enumerate(gamma_values):
            df = run_simulation(N, I0, R0, b, g, days)
            peak_infected = df["Infected"].max()
            heatmap_data[i, j] = peak_infected

    heatmap_df = pd.DataFrame(
        heatmap_data,
        index=[f"β={b:.2f}" for b in beta_values],
        columns=[f"γ={g:.2f}" for g in gamma_values]
    )

    
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_df, annot=True, fmt=".0f", cmap="viridis", ax=ax)
    ax.set_title("Peak Infected Across β–γ Combinations")
    ax.set_xlabel("Recovery Rate γ")
    ax.set_ylabel("Infection Rate β")

    st.pyplot(fig)
