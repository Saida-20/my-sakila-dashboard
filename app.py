import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set Page Dashboard Configurations
st.set_page_config(page_title="Sakila Executive Analytics Dashboard", layout="wide")
st.title("🎬 Sakila Executive Business Performance Dashboard")

# ----------------- CACHED DATA LOADING FUNCTION -----------------
@st.cache_data
def load_data():
    # Load foundational data sheets
    payment = pd.read_csv('sakila_payment.csv', sep=';')
    rental = pd.read_csv('sakila_rental.csv', sep=';')
    inventory = pd.read_csv('sakila_inventory.csv', sep=';')
    actor = pd.read_csv('sakila_actor.csv', sep=';')
    film_actor = pd.read_csv('sakila_film_actor.csv', sep=';')
    
    # Standard clean ups
    payment['amount'] = pd.to_numeric(payment['amount'], errors='coerce')
    payment['payment_date'] = pd.to_datetime(payment['payment_date'])
    rental['rental_date'] = pd.to_datetime(rental['rental_date'])
    
    # FIX: Drop 'last_update' columns to completely avoid MergeErrors
    payment_clean = payment.drop(columns=['last_update'], errors='ignore')
    rental_clean = rental.drop(columns=['last_update'], errors='ignore')
    inventory_clean = inventory.drop(columns=['last_update'], errors='ignore')
    actor_clean = actor.drop(columns=['last_update'], errors='ignore')
    film_actor_clean = film_actor.drop(columns=['last_update'], errors='ignore')
    
    return payment_clean, rental_clean, inventory_clean, actor_clean, film_actor_clean

payment, rental, inventory, actor, film_actor = load_data()

# ----------------- CREATE INTERACTIVE TABS -----------------
tab1, tab2 = st.tabs(["📉 Monthly Performance Trends", "👑 Top Performing Actors"])

with tab1:
    st.header("Monthly Macro Revenue and Volume Growth")
    
    payment['month_period'] = payment['payment_date'].dt.to_period('M')
    rental['month_period'] = rental['rental_date'].dt.to_period('M')

    rev_trend = payment.groupby('month_period')['amount'].sum().reset_index(name='revenue')
    rent_trend = rental.groupby('month_period').size().reset_index(name='rental_count')
    monthly_df = pd.merge(rev_trend, rent_trend, on='month_period', how='outer').sort_values('month_period')
    monthly_df['month_period'] = monthly_df['month_period'].astype(str)

    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    color_revenue = '#1f77b4'
    ax1.set_xlabel('Operating Timeline (Year-Month)', fontweight='bold')
    ax1.set_ylabel('Total Revenue ($)', color=color_revenue, fontweight='bold')
    ax1.plot(monthly_df['month_period'], monthly_df['revenue'], marker='o', color=color_revenue, linewidth=3)
    ax1.tick_params(axis='y', labelcolor=color_revenue)
    ax1.grid(True, linestyle=':', alpha=0.6)

    ax2 = ax1.twinx()  
    color_rentals = '#d62728'
    ax2.set_ylabel('Total Physical Rentals Placed', color=color_rentals, fontweight='bold')
    ax2.plot(monthly_df['month_period'], monthly_df['rental_count'], marker='s', linestyle='--', color=color_rentals, linewidth=3)
    ax2.tick_params(axis='y', labelcolor=color_rentals)

    plt.title('Chronological Business Scale Review', fontsize=12, fontweight='bold')
    st.pyplot(fig)

with tab2:
    st.header("Star Power Optimization Matrix")
    
    # Safe Merge Pipeline free of column collisions
    actor['actor_name'] = actor['first_name'] + ' ' + actor['last_name']
    
    rental_payment = pd.merge(rental, payment, on='rental_id', how='inner')
    rental_inv = pd.merge(rental_payment, inventory, on='inventory_id', how='inner')
    rental_film_actor = pd.merge(rental_inv, film_actor, on='film_id', how='inner')
    final_actor_df = pd.merge(rental_film_actor, actor, on='actor_id', how='inner')

    actor_stats = final_actor_df.groupby('actor_name').agg(
        total_rentals=('rental_id', 'count'),
        total_revenue=('amount', 'sum')
    ).reset_index()

    # Sidebar Filter Controls
    st.sidebar.header("Dashboard Configuration")
    top_n = st.sidebar.slider("Select Number of Top Actors:", min_value=5, max_value=20, value=10)
    metric_choice = st.radio("Performance Metric Selection:", ["Total Revenue Generated ($)", "Total Film Rental Volume"])
    
    if metric_choice == "Total Revenue Generated ($)":
        sorted_actors = actor_stats.sort_values(by='total_revenue', ascending=False).head(top_n)
        fig2, ax = plt.subplots(figsize=(8, 4))
        ax.barh(sorted_actors['actor_name'][::-1], sorted_actors['total_revenue'][::-1], color='coral', edgecolor='black')
        ax.set_title(f'Top {top_n} Actors by Revenue Field Impact')
        st.pyplot(fig2)
    else:
        sorted_actors = actor_stats.sort_values(by='total_rentals', ascending=False).head(top_n)
        fig2, ax = plt.subplots(figsize=(8, 4))
        ax.barh(sorted_actors['actor_name'][::-1], sorted_actors['total_rentals'][::-1], color='teal', edgecolor='black')
        ax.set_title(f'Top {top_n} Actors by Logistics Inventory Velocity')
        st.pyplot(fig2)