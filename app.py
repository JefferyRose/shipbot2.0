import streamlit as st
import pandas as pd


# Caching the data load
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)


# Load the data
df = load_data('star_hangar_data.csv')

# Clean the 'Price' column
df['Price'] = df['Price'].str.replace('$', '').str.replace(',', '').astype(float)

# Clean the 'Link' column by removing the duplicate prefix
df['Link'] = df['Link'].str.replace('https://star-hangar.comhttps', 'https', regex=False)


# Define the search function
def search_data(query):
    if query:
        return df[df['Name'].str.contains(query, case=False, na=False)]
    return df


# Main page title
st.title('Ship Store')

# Search bar
search_query = st.text_input("Search for a ship", value="", key="search_query", on_change=lambda: None)

# Sort by price option
sort_price = st.selectbox('Sort by Price', ['Ascending', 'Descending'])

# Shopping Cart
st.sidebar.header('Shopping Cart')
cart = st.sidebar.empty()
if 'cart_items' not in st.session_state:
    st.session_state['cart_items'] = []


def add_to_cart(ship_name, ship_price):
    st.session_state['cart_items'].append({'Name': ship_name, 'Price': ship_price})


def clear_cart():
    st.session_state['cart_items'] = []


if st.sidebar.button("Clear Cart"):
    clear_cart()

# Display filtered data based on search
filtered_df = search_data(search_query)

# Sort by price
if sort_price == 'Ascending':
    filtered_df = filtered_df.sort_values(by='Price', ascending=True)
else:
    filtered_df = filtered_df.sort_values(by='Price', ascending=False)


# Function to create clickable links
def make_clickable(val):
    return f'<a target="_blank" href="{val}">link</a>'


# Apply the clickable function to the 'Link' column
filtered_df['Link'] = filtered_df['Link'].apply(make_clickable)

# Display ships in a grid with "Add to Cart" button and link
cols = st.columns(3)[::-1]
for index, row in filtered_df.iterrows():
    with cols[index % 3]:
        st.markdown(f"{row['Link']} - ${row['Price']:.2f}", unsafe_allow_html=True)
        st.button(f'Add {row["Name"]} to Cart', key=f'add_{index}', on_click=add_to_cart,
                  args=(row['Name'], row['Price']))

# Display cart items and total price
cart_items = st.session_state['cart_items']
if cart_items:
    st.sidebar.subheader('Items in Cart')
    for item in cart_items:
        st.sidebar.write(f"{item['Name']} - ${item['Price']:.2f}")

    total_price = sum(item['Price'] for item in cart_items)
    st.sidebar.write(f"**Total: ${total_price:.2f}**")
else:
    st.sidebar.write("Your cart is empty.")
