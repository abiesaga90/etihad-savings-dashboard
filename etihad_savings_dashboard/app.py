import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Set the page configuration
st.set_page_config(page_title="Etihad Airways Savings Projection Dashboard", layout="wide")

# Set the title of the dashboard
st.title("Etihad Airways Savings Projection Dashboard")
st.markdown("""
This dashboard visualizes the projected savings for Etihad Airways over a customizable time horizon by adopting blockchain and stablecoin solutions for cash repatriation under different scenarios.
""")

# Sidebar for user input
st.sidebar.header("Dashboard Settings")

# Scenario selection
scenarios = ["Conservative Estimate", "Average Estimate", "Optimistic Estimate"]
selected_scenario = st.sidebar.selectbox("Select Scenario", scenarios)

# Define default parameters based on scenarios
default_params = {
    "Conservative Estimate": {
        "transaction_fee_percent": 3.0,
        "annual_trapped_funds": {
            "Bangladesh": 1_000_000.0,  # Converted to float
            "Pakistan": 500_000.0,
            "Others": 300_000.0
        },
        "annual_loss_rate_percent": 10.0,
        "transactions_per_year": {
            "Bangladesh": 12,
            "Pakistan": 12,
            "Others": 12
        }
    },
    "Average Estimate": {
        "transaction_fee_percent": 2.25,
        "annual_trapped_funds": {
            "Bangladesh": 1_000_000.0,
            "Pakistan": 500_000.0,
            "Others": 300_000.0
        },
        "annual_loss_rate_percent": 15.0,
        "transactions_per_year": {
            "Bangladesh": 12,
            "Pakistan": 12,
            "Others": 12
        }
    },
    "Optimistic Estimate": {
        "transaction_fee_percent": 1.5,
        "annual_trapped_funds": {
            "Bangladesh": 1_000_000.0,
            "Pakistan": 500_000.0,
            "Others": 300_000.0
        },
        "annual_loss_rate_percent": 20.0,
        "transactions_per_year": {
            "Bangladesh": 12,
            "Pakistan": 12,
            "Others": 12
        }
    }
}

# Load parameters for the selected scenario
scenario_params = default_params[selected_scenario]

# Allow users to dynamically change the transaction fee
st.sidebar.subheader("Transaction Fee Settings")
transaction_fee_percent = st.sidebar.slider(
    "Transaction Fee (%)",
    min_value=0.0,
    max_value=5.0,
    value=scenario_params["transaction_fee_percent"],
    step=0.1,
    help="Adjust the blockchain transaction fee percentage."
)

# Allow users to dynamically change the annual trapped funds
st.sidebar.subheader("Annual Trapped Funds ($)")
annual_trapped_funds = {}
for country, amount in scenario_params["annual_trapped_funds"].items():
    annual_trapped_funds[country] = st.sidebar.number_input(
        f"{country} ($)",
        min_value=0.0,
        value=float(amount),  # Ensure value is float
        step=10_000.0,        # Ensure step is float
        format="%.2f",
        help=f"Set the annual trapped funds for {country}."
    )

# Allow users to dynamically change the annual loss rate
st.sidebar.subheader("Annual Loss Rate on Trapped Cash Settings")
annual_loss_rate_percent = st.sidebar.slider(
    "Annual Loss Rate on Trapped Cash (%)",
    min_value=0.0,
    max_value=25.0,
    value=scenario_params["annual_loss_rate_percent"],
    step=0.5,
    help="Adjust the annual loss rate percentage on trapped cash."
)

# Allow users to dynamically change the one-off consulting fee
st.sidebar.subheader("Consulting Fee Settings")
consulting_fee = st.sidebar.number_input(
    "One-Off Consulting Fee ($)",
    min_value=0.0,
    value=250_000.0,    # Updated default value to float
    step=10_000.0,      # Ensure step is float
    format="%.2f",
    help="Set the one-time consulting fee for implementation."
)

# Allow users to set the number of transactions per annum per country
st.sidebar.subheader("Transaction Settings")
transactions_per_year = {}
for country, txn_default in scenario_params["transactions_per_year"].items():
    transactions_per_year[country] = st.sidebar.number_input(
        f"Number of Transactions per Year for {country}",
        min_value=1,
        max_value=100,
        value=int(txn_default),
        step=1,
        help=f"Set the number of blockchain transactions per year for {country}."
    )

# Allow users to select the time horizon
selected_years = st.sidebar.slider("Select Time Horizon (Years)", 1, 20, 10)

# Function to calculate savings
def calculate_savings(transaction_fee, trapped_funds, loss_rate, consulting_fee, years=10):
    annual_trapped_total = sum(trapped_funds.values())
    annual_current_loss = annual_trapped_total * (loss_rate / 100)
    annual_blockchain_cost = annual_trapped_total * (transaction_fee / 100)
    net_annual_savings = annual_current_loss - annual_blockchain_cost

    cumulative_savings = []
    total_savings = 0
    for year in range(1, years + 1):
        total_savings += net_annual_savings
        if year == 1:
            total_savings -= consulting_fee  # One-time consulting fee in the first year
        cumulative_savings.append(total_savings)

    return cumulative_savings, net_annual_savings, annual_current_loss, annual_blockchain_cost

# Calculate savings based on user inputs
cumulative_savings, net_annual_savings, annual_current_loss, annual_blockchain_cost = calculate_savings(
    transaction_fee=transaction_fee_percent,
    trapped_funds=annual_trapped_funds,
    loss_rate=annual_loss_rate_percent,
    consulting_fee=consulting_fee,
    years=selected_years
)

# Financial Summary Section
st.header("Financial Summary")

# Calculate payback period
payback_year = None
cumulative = 0
for year in range(1, selected_years + 1):
    if year == 1:
        cumulative += net_annual_savings - (consulting_fee / 1_000_000)
    else:
        cumulative += net_annual_savings
    if payback_year is None and cumulative >= 0:
        payback_year = year

# Calculate total savings over the selected period
total_savings_over_period = cumulative_savings[-1]

summary_df = pd.DataFrame({
    "Metric": [
        "Total Savings Over Period ($)",
        "Net Annual Savings ($)",
        "Annual Current Loss ($)",
        "Annual Blockchain Cost ($)",
        "Payback Period (Years)"
    ],
    "Value": [
        f"${total_savings_over_period:,.2f}",
        f"${net_annual_savings:,.2f}",
        f"${annual_current_loss:,.2f}",
        f"${annual_blockchain_cost:,.2f}",
        f"{payback_year if payback_year else 'Not within horizon'}"
    ]
})
st.table(summary_df)

# Cumulative Savings Over Time Section
st.header("Cumulative Savings Over Time")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(range(1, selected_years + 1)),
    y=cumulative_savings,
    mode='lines+markers',
    name='Cumulative Savings',
    line=dict(color='green')
))
fig.update_layout(
    title=f"Cumulative Savings over {selected_years} Years - {selected_scenario}",
    xaxis_title="Year",
    yaxis_title="Cumulative Savings ($)",
    template='plotly_white',
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)

# Scenario Details Section
st.header("Scenario Details")
scenario_df = pd.DataFrame({
    "Parameter": [
        "Transaction Fee (%)",
        "Annual Loss Rate on Trapped Cash (%)",
        "Consulting Fee ($)"
    ] + list(annual_trapped_funds.keys()) + list(transactions_per_year.keys()),
    "Value": [
        f"{transaction_fee_percent}%",
        f"{annual_loss_rate_percent}%",
        f"${consulting_fee:,.2f}"
    ] + [f"${amount:,.2f}" for amount in annual_trapped_funds.values()] +
    [f"{txn} transactions/year" for txn in transactions_per_year.values()]
})
st.table(scenario_df)

# Display the cumulative savings table
st.header("Yearly Cumulative Savings")
cumulative_df = pd.DataFrame({
    "Year": list(range(1, selected_years + 1)),
    "Cumulative Savings ($)": [f"${value:,.2f}" for value in cumulative_savings]
})
st.table(cumulative_df)

# Display the Transactions Assumption
st.markdown("""
---
**Assumption:** Transactions on the blockchain occur on a monthly basis (12 transactions per country per year) by default. You can adjust the number of transactions per annum for each country as needed.
""")

# Footer
st.markdown("""
---
**Data Source:** Internal financial projections based on proposed blockchain and stablecoin implementation.
""")
