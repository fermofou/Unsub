 # Load all data at the beginning
def load_all_data():
    connection = get_db_connection()
    if connection is None:
        return None, None, None
    try:
        services_query = "SELECT idS, name, link FROM services ORDER BY name"
        countries_query = "SELECT idC, name, currency FROM countries"
        prices_query =  """
            SELECT p.service_id, p.country_id, p.lev, p.price, c.currency, s.name AS service, s.link, c.name AS country
            FROM prices p
            JOIN services s ON p.service_id = s.idS
            JOIN countries c ON p.country_id = c.idC
        """
        services = pd.read_sql(services_query, connection)
        countries = pd.read_sql(countries_query, connection)
        prices = pd.read_sql(prices_query, connection)
        return services, countries, prices
    except Error as e:
        st.error(f"Error: {e}")
        return None, None, None
    finally:
        connection.close()

# Function to dynamically color the cost as it approaches the threshold
def get_color_for_value(value, max_value):
    norm = mcolors.Normalize(vmin=0, vmax=max_value)
    color = plt.cm.RdYlGn(1 - norm(value))
    return f'rgba({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)}, {color[3]})'

# Load all data at the beginning
services, countries, prices = load_all_data()

# Streamlit App
st.title("Unsubscription Manager")

# Sidebar components
st.sidebar.title("Available Services")

# Currency Selector in Sidebar with Country ID
if countries is not None:
    selected_currency_row = st.sidebar.selectbox(
        "Set Currency",
        countries.apply(lambda row: f"{row['name']} ({row['currency']})", axis=1),
        index=int(countries[countries['currency'] == 'USD'].index[0])
    )
    selected_country_id = int(countries.loc[countries.apply(lambda row: f"{row['name']} ({row['currency']})", axis=1) == selected_currency_row, 'idC'].values[0])
    currency = countries.loc[countries['idC'] == selected_country_id, 'currency'].values[0]
else:
    selected_country_id = None
    currency = "USD"  # Default currency if loading fails

# Display all services in alphabetical order
if services is not None:
    for i, service in services.iterrows():
        st.sidebar.markdown(f"### {service['name']}")
        if st.sidebar.button(f"Add {service['name']}"):
            service_id = service['idS']
            if service_id not in st.session_state["selected_services"]:
                st.session_state["selected_services"].append(service_id)
        if st.sidebar.button(f"Cancel {service['name']}"):
            service_id = service['idS']
            if service_id in st.session_state["selected_services"]:
                st.session_state["selected_services"].remove(service_id)

# Initialize session state for tracking selected services
if "selected_services" not in st.session_state:
    st.session_state["selected_services"] = []

# Display and manage subscriptions
if st.session_state["selected_services"]:
    st.subheader("Your Subscriptions")
    total_monthly = 0
    total_yearly = 0

    for service_id in st.session_state["selected_services"]:
        service_prices = prices[(prices['service_id'] == service_id) & (prices['country_id'] == selected_country_id)]
        if not service_prices.empty:
            selected_price = st.selectbox(f"Select level for {service_prices['service'].values[0]}", service_prices['lev'])

            price_row = service_prices[service_prices['lev'] == selected_price]
            monthly_cost = price_row['price'].values[0]
            yearly_cost = monthly_cost * 12

            total_monthly += monthly_cost
            total_yearly += yearly_cost

            st.write(f"**Service**: {price_row['service'].values[0]}")
            st.write(f"**Level**: {selected_price}")
            st.write(f"**Monthly Cost**: {monthly_cost} {currency}")
            st.write(f"**Yearly Cost**: {yearly_cost} {currency}")
            st.write(f"[Unsubscribe Link]({price_row['link'].values[0]})")

            # Remove service button
            if st.button(f"Remove {price_row['service'].values[0]}"):
                st.session_state["selected_services"].remove(service_id)

    # Dynamic color coding for total cost as it approaches threshold
    monthly_color = get_color_for_value(total_monthly, 100)
    yearly_color = get_color_for_value(total_yearly, 1200)

    st.markdown(f"<h3 style='color:{monthly_color}'>Total Monthly Cost: {total_monthly} {currency}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{yearly_color}'>Total Yearly Cost: {total_yearly} {currency}</h3>", unsafe_allow_html=True)
 