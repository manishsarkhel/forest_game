import streamlit as st
import pandas as pd
import numpy as np

# --- Simulation Core Logic ---
def run_simulation(
    periods,
    initial_forest_stock,
    regeneration_rate_percentage,
    annual_harvest_target,
    production_capacity_per_period,
    timber_per_product,
    demand_per_period,
    selling_price_per_product,
    harvesting_cost_per_ton,
    production_cost_per_product,
    holding_cost_timber_per_ton,
    holding_cost_product_per_unit
):
    """
    Runs the forest operations simulation.
    """
    # Initialize data tracking lists
    forest_stock_over_time = []
    harvested_timber_over_time = []
    timber_inventory_over_time = []
    products_produced_over_time = []
    finished_goods_inventory_over_time = []
    demand_over_time = []
    sales_over_time = []
    revenue_over_time = []
    total_cost_over_time = []
    profit_over_time = []
    cumulative_profit_over_time = []

    # Initial state
    current_forest_stock = initial_forest_stock
    current_timber_inventory = 0  # Start with no timber inventory
    current_finished_goods_inventory = 0 # Start with no finished goods inventory
    current_cumulative_profit = 0
    regeneration_rate = regeneration_rate_percentage / 100.0

    for period in range(1, periods + 1):
        # 1. Forest Regeneration
        # Forest regenerates at the beginning of the period on the *remaining* stock
        forest_growth = current_forest_stock * regeneration_rate
        current_forest_stock += forest_growth
        current_forest_stock = max(0, current_forest_stock) # Cannot be negative

        # 2. Harvesting
        # Harvest based on target, but limited by available forest stock
        actual_harvest = min(annual_harvest_target, current_forest_stock)
        current_forest_stock -= actual_harvest
        current_timber_inventory += actual_harvest # Harvested timber goes to inventory

        # 3. Production
        # Produce based on capacity, but limited by available timber inventory
        potential_production_from_timber = current_timber_inventory / timber_per_product
        actual_production = min(production_capacity_per_period, potential_production_from_timber)
        
        timber_consumed = actual_production * timber_per_product
        current_timber_inventory -= timber_consumed
        current_finished_goods_inventory += actual_production

        # 4. Demand & Sales
        # For simplicity, demand is constant in this version
        current_demand = demand_per_period
        
        # Sales are limited by available finished goods inventory and demand
        actual_sales = min(current_finished_goods_inventory, current_demand)
        current_finished_goods_inventory -= actual_sales

        # 5. Calculate Revenue & Costs
        revenue = actual_sales * selling_price_per_product
        
        cost_harvesting = actual_harvest * harvesting_cost_per_ton
        cost_production = actual_production * production_cost_per_product
        cost_holding_timber = current_timber_inventory * holding_cost_timber_per_ton
        cost_holding_products = current_finished_goods_inventory * holding_cost_product_per_unit
        
        total_period_cost = cost_harvesting + cost_production + cost_holding_timber + cost_holding_products
        
        # 6. Calculate Profit
        period_profit = revenue - total_period_cost
        current_cumulative_profit += period_profit

        # 7. Store period data
        forest_stock_over_time.append(current_forest_stock)
        harvested_timber_over_time.append(actual_harvest)
        timber_inventory_over_time.append(current_timber_inventory)
        products_produced_over_time.append(actual_production)
        finished_goods_inventory_over_time.append(current_finished_goods_inventory)
        demand_over_time.append(current_demand)
        sales_over_time.append(actual_sales)
        revenue_over_time.append(revenue)
        total_cost_over_time.append(total_period_cost)
        profit_over_time.append(period_profit)
        cumulative_profit_over_time.append(current_cumulative_profit)

    # Create a DataFrame for results
    results_df = pd.DataFrame({
        "Period": range(1, periods + 1),
        "Forest Stock (tons)": forest_stock_over_time,
        "Harvested Timber (tons)": harvested_timber_over_time,
        "Timber Inventory (tons)": timber_inventory_over_time,
        "Products Produced (units)": products_produced_over_time,
        "Finished Goods Inventory (units)": finished_goods_inventory_over_time,
        "Demand (units)": demand_over_time,
        "Sales (units)": sales_over_time,
        "Revenue ($)": revenue_over_time,
        "Total Cost ($)": total_cost_over_time,
        "Period Profit ($)": profit_over_time,
        "Cumulative Profit ($)": cumulative_profit_over_time,
    })
    return results_df

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🌲 Forest Operations & Sustainability Simulator 🏭")

st.markdown("""
This simulator helps visualize the impact of operational decisions on a forest resource and company profitability.
Adjust the parameters in the sidebar and click "Run Simulation" to see the results.
This model is inspired by challenges similar to those faced by Priya at Neev Living, balancing growth with resource sustainability.
""")

# --- Sidebar for Inputs ---
st.sidebar.header("⚙️ Simulation Parameters")

sim_periods = st.sidebar.slider("Number of Simulation Periods (e.g., Years)", 5, 50, 20)
init_stock = st.sidebar.number_input("Initial Forest Stock (tons)", min_value=1000, max_value=1000000, value=50000, step=1000)
regen_rate = st.sidebar.slider("Forest Regeneration Rate (% per period)", 0.0, 20.0, 5.0, 0.1)

st.sidebar.subheader("Harvesting & Production Decisions")
harvest_target = st.sidebar.number_input("Annual Harvest Target (tons)", min_value=0, max_value=int(init_stock*0.5), value=2500, step=100) # Sensible max
prod_capacity = st.sidebar.number_input("Production Capacity (units of finished product/period)", min_value=0, max_value=10000, value=1000, step=50)
timber_per_prod = st.sidebar.number_input("Timber per Product (tons/unit)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)

st.sidebar.subheader("Market & Financials")
demand_rate = st.sidebar.number_input("Demand per Period (units)", min_value=0, max_value=10000, value=800, step=50)
sell_price = st.sidebar.number_input("Selling Price per Product ($)", min_value=0, max_value=1000, value=200, step=10)
harvest_cost = st.sidebar.number_input("Harvesting Cost per Ton of Timber ($)", min_value=0, max_value=200, value=20, step=1)
prod_cost = st.sidebar.number_input("Production Cost per Product ($)", min_value=0, max_value=500, value=50, step=5) # Excludes timber cost
holding_cost_timber = st.sidebar.number_input("Holding Cost per Ton of Timber ($/period)", min_value=0.0, max_value=20.0, value=1.0, step=0.1)
holding_cost_product = st.sidebar.number_input("Holding Cost per Product Unit ($/period)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)

# --- Simulation Execution ---
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

if st.sidebar.button("🚀 Run Simulation"):
    results = run_simulation(
        sim_periods, init_stock, regen_rate, harvest_target,
        prod_capacity, timber_per_prod, demand_rate,
        sell_price, harvest_cost, prod_cost,
        holding_cost_timber, holding_cost_product
    )
    st.session_state.simulation_results = results

# --- Display Results ---
if st.session_state.simulation_results is not None:
    results_df = st.session_state.simulation_results
    st.header("📊 Simulation Results")

    # Key Metrics
    st.subheader("📈 Key Performance Indicators (End of Simulation)")
    col1, col2, col3, col4 = st.columns(4)
    final_forest_stock = results_df["Forest Stock (tons)"].iloc[-1]
    total_profit = results_df["Cumulative Profit ($)"].iloc[-1]
    
    col1.metric("Final Forest Stock (tons)", f"{final_forest_stock:,.0f}")
    col2.metric("Total Cumulative Profit ($)", f"${total_profit:,.0f}")
    
    total_harvested = results_df["Harvested Timber (tons)"].sum()
    col3.metric("Total Timber Harvested (tons)", f"{total_harvested:,.0f}")
    
    total_sales_units = results_df["Sales (units)"].sum()
    col4.metric("Total Products Sold (units)", f"{total_sales_units:,.0f}")

    # Charts
    st.subheader("📉 Charts Over Time")
    
    st.line_chart(results_df.set_index("Period")[["Forest Stock (tons)"]])
    st.caption("Forest Stock: Shows the remaining timber in the forest over time. A steep decline indicates unsustainable harvesting.")
    
    st.line_chart(results_df.set_index("Period")[["Cumulative Profit ($)"]])
    st.caption("Cumulative Profit: Tracks the total profit accumulated. Consider this alongside forest stock for a complete picture of sustainability.")

    inventory_cols = ["Timber Inventory (tons)", "Finished Goods Inventory (units)"]
    st.line_chart(results_df.set_index("Period")[inventory_cols])
    st.caption("Inventory Levels: Shows raw timber and finished product inventories. High inventories incur holding costs.")

    production_sales_cols = ["Products Produced (units)", "Sales (units)", "Demand (units)"]
    st.line_chart(results_df.set_index("Period")[production_sales_cols])
    st.caption("Production, Sales, and Demand: Compares production output, actual sales, and market demand.")
    
    st.subheader("📄 Detailed Results Table")
    st.dataframe(results_df.style.format({
        "Forest Stock (tons)": "{:,.0f}",
        "Harvested Timber (tons)": "{:,.0f}",
        "Timber Inventory (tons)": "{:,.0f}",
        "Products Produced (units)": "{:,.0f}",
        "Finished Goods Inventory (units)": "{:,.0f}",
        "Demand (units)": "{:,.0f}",
        "Sales (units)": "{:,.0f}",
        "Revenue ($)": "${:,.2f}",
        "Total Cost ($)": "${:,.2f}",
        "Period Profit ($)": "${:,.2f}",
        "Cumulative Profit ($)": "${:,.2f}",
    }))
    
    # Discussion points related to the case study
    st.subheader("🤔 Discussion Points (Relating to Priya's Dilemma)")
    st.markdown(f"""
    * **Unsustainable Harvesting:** If the "Forest Stock (tons)" chart shows a rapid decline to near zero, this mirrors the "race to the bottom" scenario. What would be the long-term impact on Neev Living if their supplier (like Vanashakti) operated this way?
    * **Cost vs. Sustainability:** Experiment with the `Annual Harvest Target`. A higher target might boost short-term profit but deplete the forest faster. How does this relate to Priya's pressure to find a *cost-effective* solution?
    * **Regeneration Rate:** A low `Forest Regeneration Rate` makes sustainable harvesting much harder. This is akin to operating in a region with poor natural recovery or weak governance for reforestation.
    * **Long-term Viability:** Is maximizing short-term profit always the best strategy if it destroys the resource base? How does this simulation help understand the risks Priya might be overlooking if she only focuses on Vanashakti's low price?
    * **Inventory Costs:** Notice how holding costs for timber and finished products affect profitability. Efficient operations try to minimize these without stocking out.
    """)

else:
    st.info("Adjust parameters in the sidebar and click 'Run Simulation' to see the results.")

st.sidebar.markdown("---")
st.sidebar.markdown("Inspired by the case study: 'Priya's Timber Dilemma at Neev Living'")
