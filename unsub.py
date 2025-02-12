import os 
import mysql.connector
import pandas as pd
from mysql.connector import Error
from dotenv import load_dotenv

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import streamlit as st
import altair as alt
import numpy as np

# Streamlit UI header
st.title("UnsubMe")

# Define services and their subscription levels with corresponding monthly costs
services = {
    'Disney+': {'Basic: $8': 8, 'Premium: $11': 11},
    'Netflix': {'Basic: $7': 7, 'Standard: $15': 15, 'Premium: $23': 23},
    'Amazon Prime': {'Monthly: $7': 8, 'Extra: $10': 15},
    'Spotify': {'Free': 0, 'Premium': 10}
}

# Create columns for each service
columns = st.columns(len(services))
selected_subscriptions = {}

servicesLinks = {
    'Disney+': 'https://www.disneyplus.com/cancel-subscription',
    'Netflix': 'https://www.netflix.com/account/membership',
    'Amazon Prime':'https://www.amazon.com/gp/video/settings',
    'Spotify': 'https://www.spotify.com/mx/account/cancel'
}

for (service, options), col in zip(services.items(), columns):
    with col:
        show_options = st.checkbox(f'Show {service} options')
        if show_options:
            levels = list(options.keys())
            default_level = levels[0]
            selected_level = st.selectbox(f'Subscription Level:', levels, index=0)
            selected_subscriptions[service] = options[selected_level]
        
        if servicesLinks[service]:
            st.markdown(
                f'<a href="{servicesLinks[service]}" target="_blank">'
                f'<button style="width:100%; background-color: red; border-radius: 15px; padding: 10px; color: white;">Unsub Me</button></a>',
                unsafe_allow_html=True
            )

# User input for monthly budget
myBudget = st.slider("My Budget per month ($):", 1, 150, 50)

# Calculate costs
individual_costs = pd.DataFrame(list(selected_subscriptions.items()), columns=['Service', 'Monthly Cost'])
total_monthly_cost = individual_costs['Monthly Cost'].sum()
st.write(f"### **Total Monthly Cost: ${total_monthly_cost}**")

# Pie chart parameters
total_cost = total_monthly_cost
service_names = list(selected_subscriptions.keys())
service_costs = list(selected_subscriptions.values())
# Calculate how many pies are needed (each pie represents a slice of the budget)
num_pies = int(total_cost // myBudget) + (1 if total_cost % myBudget > 0 else 0)
if (num_pies>1):
    st.write(f"### **Damn u r overbudget**")
else:
    st.write(f"### **My Budget**")

# Define colors
colors = ['#1E90FF', '#8A2BE2', '#FFD700', '#FF8C00', '#FF69B4']
free_money_color = '#66ff66'  # Green for unused money
transparent_color = (0, 0, 0, 0)  # Fully transparent (RGBA)

# Prepare list to store pie chart figures
pie_figs = []
start_index = 0

# Generate pie charts
# Note: We make a copy of service_costs so that we can deduct amounts per pie
service_costs_copy = service_costs.copy()

for i in range(num_pies):
    fig, ax = plt.subplots()
    remaining_budget = myBudget
    pie_labels, pie_sizes, pie_colors = [], [], []
    
    # Fill the current pie with slices from the services until budget runs out
    while start_index < len(service_costs_copy) and remaining_budget > 0:
        cost = service_costs_copy[start_index]
        if cost <= remaining_budget:
            pie_labels.append(service_names[start_index])
            pie_sizes.append(cost)
            pie_colors.append(colors[start_index % len(colors)])
            remaining_budget -= cost
            start_index += 1
        else:
            pie_labels.append(service_names[start_index])
            pie_sizes.append(remaining_budget)
            pie_colors.append(colors[start_index % len(colors)])
            service_costs_copy[start_index] -= remaining_budget
            remaining_budget = 0

    # After filling with service slices, decide what to do with any remaining budget:
    if total_cost <= myBudget and remaining_budget > 0:
        # Under budget: display the unused money as "Free Money"
        pie_labels.append("Free Money")
        pie_sizes.append(remaining_budget)
        pie_colors.append(free_money_color)
    elif total_cost > myBudget and remaining_budget > 0 and i == num_pies - 1:
        # Over budget: on the last pie, mark the remaining amount as "Over Budget"
        pie_labels.append("Over Budget")
        pie_sizes.append(remaining_budget)
        # Set the "Over Budget" slice to be transparent
        pie_colors.append(transparent_color)
    
    ## Create the pie chart without external labels
    fig, ax = plt.subplots()

    # Create pie chart and capture the wedge objects and autopct texts
    wedges, autotexts, _ = ax.pie(
    pie_sizes,
    labels=None,  # Omit labels here to prevent them from being drawn outside
    autopct=lambda pct: f'${pct * sum(pie_sizes) / 100:.1f}',  # Cost inside the slice
    colors=pie_colors,
    wedgeprops={'edgecolor': (0, 0, 0, 0)},
    textprops={'color': (14/255, 17/255, 23/255, 1), 'fontsize': 10},
    pctdistance=0.6  # Adjust this to control the position of the autopct text
    )

    for i, wedge in enumerate(wedges):
    # Compute the angle in degrees of the center of the wedge
        angle = (wedge.theta2 + wedge.theta1) / 2.0
    # Convert angle to radians for placement
        x = np.cos(np.deg2rad(angle)) * 0.30
        y = np.sin(np.deg2rad(angle)) * 0.37
        ax.text(
            x, y,
            pie_labels[i],
            horizontalalignment='center',
            verticalalignment='center',
            color=(14/255, 17/255, 23/255, 1),
            fontsize=10
        )

    fig.patch.set_facecolor((14/255, 17/255, 23/255, 1))
    pie_figs.append(fig)


# Display the pie charts side by side (in rows of 2)
for i in range(0, len(pie_figs), 2):
    cols = st.columns(2)
    cols[0].pyplot(pie_figs[i])
    if i + 1 < len(pie_figs):
        cols[1].pyplot(pie_figs[i + 1])
