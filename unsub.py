# Streamlit and pandas are required
import streamlit as st
import pandas as pd

# Optional: For real-time currency conversion (mock data used here for simplicity)
from forex_python.converter import CurrencyRates

# Initialize a global dataframe to store subscriptions
if 'subscriptions' not in st.session_state:
    st.session_state.subscriptions = pd.DataFrame(columns=["Name", "Price (USD)", "Frequency", "Link", "Price in Local Currency"])

# Define a function to simulate currency conversion
def convert_to_local(price_usd, local_currency="USD"):
    # Normally, you would use a library like forex-python for real-time conversion
    # For now, we're mocking the conversion rate to be 1:1
    conversion_rate = 1  # Mock conversion rate
    return round(price_usd * conversion_rate, 2)

# Sidebar: Form to add a new subscription
st.sidebar.header("Add New Subscription")
name = st.sidebar.text_input("Subscription Name")
price = st.sidebar.number_input("Price (USD)", min_value=0.0, step=0.1)
frequency = st.sidebar.selectbox("Frequency", ["Monthly", "Yearly"])
link = st.sidebar.text_input("Link (Optional)")
local_currency = "USD"  # Modify based on the user's country or let the user choose

# Add button to save the subscription
if st.sidebar.button("Add Subscription"):
    # Convert the price to local currency (mocking here for simplicity)
    local_price = convert_to_local(price, local_currency)
    
    # Add to the DataFrame
    new_subscription = pd.DataFrame({
        "Name": [name],
        "Price (USD)": [price],
        "Frequency": [frequency],
        "Link": [link],
        "Price in Local Currency": [f"{local_price} {local_currency}"]
    })
    st.session_state.subscriptions = pd.concat([st.session_state.subscriptions, new_subscription], ignore_index=True)
    st.sidebar.success(f"{name} added!")

# Main app
st.title("Unsub")

# Display subscriptions
st.subheader("Your Subscriptions")
if not st.session_state.subscriptions.empty:
    for idx, row in st.session_state.subscriptions.iterrows():
        # Display subscription details
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        col1.write(f"**{row['Name']}**")
        col2.write(f"${row['Price (USD)']:.2f}")
        col3.write(row["Frequency"])
        
        # Button to open the link
        if row["Link"]:
            col4.write(f"[Manage]({row['Link']})")

    # Calculate and display the total cost per month and per year
    monthly_total = st.session_state.subscriptions.apply(
        lambda x: x["Price (USD)"] if x["Frequency"] == "Monthly" else x["Price (USD)"] / 12,
        axis=1
    ).sum()
    yearly_total = st.session_state.subscriptions.apply(
        lambda x: x["Price (USD)"] * 12 if x["Frequency"] == "Yearly" else x["Price (USD)"] * 12,
        axis=1
    ).sum()
    
    st.write("### Total Cost")
    st.write(f"**Monthly:** ${monthly_total:.2f}")
    st.write(f"**Yearly:** ${yearly_total:.2f}")

else:
    st.write("No subscriptions added yet.")

# Delete option
st.subheader("Manage Subscriptions")
delete_name = st.text_input("Enter subscription name to delete")
if st.button("Delete Subscription"):
    st.session_state.subscriptions = st.session_state.subscriptions[st.session_state.subscriptions["Name"] != delete_name]
    st.success(f"{delete_name} deleted.")
