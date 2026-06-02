import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Page Configuration Setup
st.set_page_config(page_title="Sakila Comprehensive Data Dashboard", layout="wide")
st.title("🎬 Sakila Enterprise Business Intelligence Dashboard")
st.markdown("Interactive performance evaluation system mapping operational logistics, sales metrics, and rental trends.")
st.write("---")

# 2. Optimized Data Ingestion with Merging Safeguards
@st.cache_data
def load_and_clean_sakila_data():
    # Load required transactional database logs
    payment = pd.read_csv('sakila_payment.csv', sep=';')
    rental = pd.read_csv('sakila_rental.csv', sep=';')
    inventory = pd.read_csv('sakila_inventory.csv', sep=';')
    actor = pd.read_csv('sakila_actor.csv', sep=';')
    film_actor = pd.read_csv('sakila_film_actor.csv', sep=';')
    customer = pd.read_csv('sakila_customer.csv', sep=';')
    film_category = pd.read_csv('sakila_film_category.csv', sep=';')
    category = pd.read_csv('sakila_category.csv', sep=';')
    
    # Standard Data Type Normalization
    payment['amount'] = pd.to_numeric(payment['amount'], errors='coerce')
    payment['payment_date'] = pd.to_datetime(payment['payment_date'])
    rental['rental_date'] = pd.to_datetime(rental['rental_date'])
    
    # SAFEGUARD: Drop the redundant administrative timestamp columns 
    # to completely avoid the pandas.errors.MergeError column collision
    p_clean = payment.drop(columns=['last_update'], errors='ignore')
    r_clean = rental.drop(columns=['last_update'], errors='ignore')
    i_clean = inventory.drop(columns=['last_update'], errors='ignore')
    a_clean = actor.drop(columns=['last_update'], errors='ignore')
    fa_clean = film_actor.drop(columns=['last_update'], errors='ignore')
    c_clean = customer.drop(columns=['last_update'], errors='ignore')
    fc_clean = film_category.drop(columns=['last_update'], errors='ignore')
    cat_clean = category.drop(columns=['last_update'], errors='ignore')
    
    return p_clean, r_clean, i_clean, a_clean, fa_clean, c_clean, fc_clean, cat_clean

# Unpack clean operational datasets
payment, rental, inventory, actor, film_actor, customer, film_category, category = load_and_clean_sakila_data()

# 3. Create Modern Tab-Driven Workspace Navigator
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👥 Customer Rentals", 
    "📁 Category Revenue", 
    "🏪 Store Performance", 
    "📈 Monthly Trends", 
    "🎭 Actor Popularity"
])

# ----------------- TASK 1: CUSTOMER RENTAL ANALYSIS -----------------
with tab1:
    st.header("Task 1: Customer Rental Analysis")
    st.markdown("Identify the top customers with the highest number of movie rentals and total amount spent.")
    
    cust_rentals = rental.groupby('customer_id').size().reset_index(name='total_rentals')
    cust_payments = payment.groupby('customer_id')['amount'].sum().reset_index(name='total_spent')
    cust_merged = pd.merge(pd.merge(cust_rentals, cust_payments, on='customer_id'), customer, on='customer_id')
    cust_merged['customer_name'] = cust_merged['first_name'] + ' ' + cust_merged['last_name']
    
    top_customers = cust_merged.sort_values(by='total_rentals', ascending=False).head(10)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Top 10 Consumer Metrics Table")
        st.dataframe(top_customers[['customer_name', 'total_rentals', 'total_spent']], use_container_width=True)
    with col2:
        st.subheader("Total Revenue Yield by Top Customer Profile")
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.barh(top_customers['customer_name'][::-1], top_customers['total_spent'][::-1], color='#3182bd', edgecolor='black')
        ax.set_xlabel('Total Dollars Contributed ($)')
        st.pyplot(fig)

# ----------------- TASK 2: FILM CATEGORY REVENUE ANALYSIS -----------------
with tab2:
    st.header("Task 2: Film Category Revenue Analysis")
    st.markdown("Determine which movie categories generate the highest revenue and rental frequency.")
    
    m1 = pd.merge(payment, rental, on='rental_id', how='inner')
    m2 = pd.merge(m1, inventory, on='inventory_id', how='inner')
    m3 = pd.merge(m2, film_category, on='film_id', how='inner')
    cat_final = pd.merge(m3, category, on='category_id', how='inner')
    
    cat_summary = cat_final.groupby('name').agg(
        total_revenue=('amount', 'sum'),
        rental_frequency=('rental_id', 'count')
    ).reset_index().sort_values(by='total_revenue', ascending=False)
    
    st.subheader("Category Sales Distribution Performance Matrix")
    st.dataframe(cat_summary, use_container_width=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.bar(cat_summary['name'], cat_summary['total_revenue'], color='indigo', edgecolor='black')
    ax1.set_title('Gross Corporate Revenue Generation ($)')
    ax1.set_xticklabels(cat_summary['name'], rotation=45, ha='right')
    
    cat_freq = cat_summary.sort_values(by='rental_frequency', ascending=False)
    ax2.bar(cat_freq['name'], cat_freq['rental_frequency'], color='teal', edgecolor='black')
    ax2.set_title('Logistics Rental Checkout Volumetric Count')
    ax2.set_xticklabels(cat_freq['name'], rotation=45, ha='right')
    st.pyplot(fig)

# ----------------- TASK 3: STORE PERFORMANCE EVALUATION -----------------
with tab3:
    st.header("Task 3: Store Performance Evaluation")
    st.markdown("Compare the performance of the two stores based on revenue, number of customers, and rentals processed.")
    
    store_rent_payment = pd.merge(pd.merge(rental, payment, on='rental_id'), inventory, on='inventory_id')
    store_perf = store_rent_payment.groupby('store_id').agg(
        total_revenue=('amount', 'sum'),
        rentals_processed=('rental_id', 'count')
    ).reset_index()
    
    store_cust = customer.groupby('store_id').size().reset_index(name='registered_customers')
    store_final_dashboard = pd.merge(store_perf, store_cust, on='store_id')
    store_final_dashboard['store_id'] = store_final_dashboard['store_id'].map({1: "Store 1 (Lethbridge)", 2: "Store 2 (Woodridge)"})
    
    # Modern Executive KPI Metrics display
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Global Lifetime Revenue Yield", f"${payment['amount'].sum():,.2f}")
    kpi2.metric("Total Operational Volume", f"{rental.shape[0]:,} Rentals")
    kpi3.metric("Total Active Customer Footprint", f"{customer.shape[0]} Users")
    
    st.write("---")
    st.subheader("Comparative Retail Metrics Breakdown")
    st.dataframe(store_final_dashboard, use_container_width=True)

# ----------------- TASK 4: MONTHLY REVENUE TREND ANALYSIS -----------------
with tab4:
    st.header("Task 4: Monthly Revenue Trend Analysis")
    st.markdown("Analyze monthly revenue trends and identify peak rental periods.")
    
    payment['month_period'] = payment['payment_date'].dt.to_period('M')
    rental['month_period'] = rental['rental_date'].dt.to_period('M')

    rev_trend = payment.groupby('month_period')['amount'].sum().reset_index(name='revenue')
    rent_trend = rental.groupby('month_period').size().reset_index(name='rental_count')
    monthly_df = pd.merge(rev_trend, rent_trend, on='month_period', how='outer').sort_values('month_period')
    monthly_df['month_period'] = monthly_df['month_period'].astype(str)

    fig, ax1 = plt.subplots(figsize=(11, 4.5))
    color_revenue = '#1f77b4'
    ax1.set_xlabel('Operating Timeline (Year-Month)', fontweight='bold')
    ax1.set_ylabel('Total Monthly Revenue ($)', color=color_revenue, fontweight='bold')
    ax1.plot(monthly_df['month_period'], monthly_df['revenue'], marker='o', color=color_revenue, linewidth=3)
    ax1.tick_params(axis='y', labelcolor=color_revenue)
    ax1.grid(True, linestyle=':', alpha=0.6)

    ax2 = ax1.twinx()  
    color_rentals = '#d62728'
    ax2.set_ylabel('Total Physical Rentals Placed', color=color_rentals, fontweight='bold')
    ax2.plot(monthly_df['month_period'], monthly_df['rental_count'], marker='s', linestyle='--', color=color_rentals, linewidth=3)
    ax2.tick_params(axis='y', labelcolor=color_rentals)

    plt.title('Chronological Growth Cycle Review', fontsize=12, fontweight='bold')
    st.pyplot(fig)

# ----------------- TASK 5: ACTOR POPULARITY AND FILM PERFORMANCE -----------------
with tab5:
    st.header("Task 5: Actor Popularity and Film Performance")
    st.markdown("Identify the actors appearing in the highest number of rented films and evaluate the revenue generated by their movies.")
    
    actor['actor_name'] = actor['first_name'] + ' ' + actor['last_name']
    
    # Secure relational pipeline
    r_p = pd.merge(rental, payment, on='rental_id', how='inner')
    r_i = pd.merge(r_p, inventory, on='inventory_id', how='inner')
    r_fa = pd.merge(r_i, film_actor, on='film_id', how='inner')
    final_actor_df = pd.merge(r_fa, actor, on='actor_id', how='inner')

    actor_stats = final_actor_df.groupby('actor_name').agg(
        total_rentals=('rental_id', 'count'),
        total_revenue=('amount', 'sum')
    ).reset_index()

    # Dynamic Dashboard User Controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("Task 5 Filter Configurations")
    top_n = st.sidebar.slider("Select Actor Density Range Window:", min_value=5, max_value=25, value=10)
    metric_choice = st.radio("Primary Evaluation KPI:", ["Total Revenue Generated ($)", "Total Film Rental Volume"])
    
    if metric_choice == "Total Revenue Generated ($)":
        sorted_actors = actor_stats.sort_values(by='total_revenue', ascending=False).head(top_n)
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.barh(sorted_actors['actor_name'][::-1], sorted_actors['total_revenue'][::-1], color='coral', edgecolor='black')
        ax.set_title(f'Top {top_n} Actors Sorted by Portfolio Financial Returns Impact')
        ax.set_xlabel('Total Business Revenue ($)')
        st.pyplot(fig)
    else:
        sorted_actors = actor_stats.sort_values(by='total_rentals', ascending=False).head(top_n)
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.barh(sorted_actors['actor_name'][::-1], sorted_actors['total_rentals'][::-1], color='darkcyan', edgecolor='black')
        ax.set_title(f'Top {top_n} Actors Sorted by Checkout Volume Generation')
        ax.set_xlabel('Total Physical Rental Count')
        st.pyplot(fig)