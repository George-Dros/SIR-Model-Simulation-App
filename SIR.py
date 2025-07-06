import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

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
st.sidebar.header("Simulation Parameters")
sensitivity = st.sidebar.checkbox("Run Sensitivity Analysis")
N = st.sidebar.slider("Total Population (N)", 100, 1000000, 10000, step=100)
I0 = st.sidebar.slider("Initial Infected (I₀)", 1, N // 10, 10)
R0 = st.sidebar.slider("Initial Recovered (R₀)", 0, N // 10, 0)
beta = st.sidebar.slider("Infection Rate (β)", 0.0, 1.0, 0.3, step=0.01)
gamma = st.sidebar.slider("Recovery Rate (γ)", 0.0, 1.0, 0.1, step=0.01)
days = st.sidebar.slider("Simulation Duration (days)", 10, 365, 160)

if sensitivity:
    
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

else:
    # run single simulation
    df = run_simulation(N, I0, R0, beta, gamma, days)

    # Plot
    st.write("### Infection Curve")
    st.line_chart(df.set_index("Day"))

    # Final numbers
    st.write("### Final State")
    st.write(df.iloc[-1])


