import streamlit as st
import random

# --- Game Configuration ---
INITIAL_MONEY = 100000
INITIAL_TIMBER_IN_FOREST = 5000  # Units of timber
FOREST_GROWTH_RATE_PER_TURN = 0.02  # 2% growth per turn
MAX_HARVEST_PER_TURN = 500
HARVEST_COST_PER_UNIT = 10
TRANSPORT_COST_PER_UNIT_TIMBER = 5 # Cost to transport from forest to mill

MILL_CAPACITY_PER_TURN = 300  # Units of timber it can process
PROCESSING_COST_PER_UNIT_TIMBER = 15 # Cost to process 1 unit of timber
TIMBER_TO_PRODUCT_RATIO = 0.8  # 1 unit of timber yields 0.8 units of product (e.g., lumber)

INITIAL_PRODUCT_PRICE = 50
PRICE_FLUCTUATION_RANGE = 10 # Price can go up or down by this amount
DEMAND_FLUCTUATION_RANGE_PERCENT = 0.2 # Demand can fluctuate by +/- 20%
INITIAL_MARKET_DEMAND = 200 # Units of product

# --- Helper Functions ---
def initialize_game():
    """Initializes or resets the game state."""
    st.session_state.money = INITIAL_MONEY
    st.session_state.timber_in_forest = INITIAL_TIMBER_IN_FOREST
    st.session_state.harvested_timber_inventory = 0 # At the forest, pre-transport
    st.session_state.mill_timber_inventory = 0 # Timber at the mill
    st.session_state.processed_product_inventory = 0
    st.session_state.current_turn = 1
    st.session_state.product_price = INITIAL_PRODUCT_PRICE
    st.session_state.market_demand = INITIAL_MARKET_DEMAND
    st.session_state.logs = ["Game initialized."]
    st.session_state.game_over = False
    st.session_state.win_condition_met = False

def add_log(message):
    """Adds a message to the game log."""
    st.session_state.logs.insert(0, f"Turn {st.session_state.current_turn}: {message}")
    if len(st.session_state.logs) > 20: # Keep log size manageable
        st.session_state.logs.pop()

# --- Game Logic Functions ---
def harvest_timber(amount_to_harvest):
    """Handles harvesting timber from the forest."""
    if st.session_state.game_over: return
    if amount_to_harvest <= 0:
        add_log("No timber harvested.")
        return

    actual_harvested = min(amount_to_harvest, st.session_state.timber_in_forest, MAX_HARVEST_PER_TURN)
    cost = actual_harvested * HARVEST_COST_PER_UNIT

    if st.session_state.money < cost:
        add_log(f"Not enough money to harvest {actual_harvested} units. Cost: ${cost:.2f}")
        return

    st.session_state.timber_in_forest -= actual_harvested
    st.session_state.harvested_timber_inventory += actual_harvested
    st.session_state.money -= cost
    add_log(f"Harvested {actual_harvested} units of timber. Cost: ${cost:.2f}. Money left: ${st.session_state.money:.2f}")

def transport_timber_to_mill(amount_to_transport):
    """Handles transporting timber from forest inventory to mill inventory."""
    if st.session_state.game_over: return
    if amount_to_transport <= 0:
        add_log("No timber transported.")
        return

    actual_transported = min(amount_to_transport, st.session_state.harvested_timber_inventory)
    cost = actual_transported * TRANSPORT_COST_PER_UNIT_TIMBER

    if st.session_state.money < cost:
        add_log(f"Not enough money to transport {actual_transported} units. Cost: ${cost:.2f}")
        return

    st.session_state.harvested_timber_inventory -= actual_transported
    st.session_state.mill_timber_inventory += actual_transported
    st.session_state.money -= cost
    add_log(f"Transported {actual_transported} units of timber to mill. Cost: ${cost:.2f}. Money left: ${st.session_state.money:.2f}")


def process_timber(amount_to_process):
    """Handles processing timber at the mill."""
    if st.session_state.game_over: return
    if amount_to_process <= 0:
        add_log("No timber processed.")
        return

    actual_processed = min(amount_to_process, st.session_state.mill_timber_inventory, MILL_CAPACITY_PER_TURN)
    cost = actual_processed * PROCESSING_COST_PER_UNIT_TIMBER

    if st.session_state.money < cost:
        add_log(f"Not enough money to process {actual_processed} units. Cost: ${cost:.2f}")
        return

    st.session_state.mill_timber_inventory -= actual_processed
    st.session_state.money -= cost
    product_yield = actual_processed * TIMBER_TO_PRODUCT_RATIO
    st.session_state.processed_product_inventory += product_yield
    add_log(f"Processed {actual_processed} units of timber, yielding {product_yield:.2f} units of product. Cost: ${cost:.2f}. Money left: ${st.session_state.money:.2f}")

def sell_product(amount_to_sell):
    """Handles selling processed products to the market."""
    if st.session_state.game_over: return

    if amount_to_sell <= 0:
        add_log("No product sold.")
        return

    # Player can't sell more than they have or more than the market demands
    actual_sold = min(amount_to_sell, st.session_state.processed_product_inventory, st.session_state.market_demand)
    revenue = actual_sold * st.session_state.product_price

    st.session_state.processed_product_inventory -= actual_sold
    st.session_state.money += revenue
    st.session_state.market_demand -= actual_sold # Reduce demand for this turn
    add_log(f"Sold {actual_sold:.2f} units of product for ${revenue:.2f}. Money: ${st.session_state.money:.2f}")

def next_turn():
    """Advances the game to the next turn."""
    if st.session_state.game_over: return

    st.session_state.current_turn += 1

    # Forest growth
    growth = st.session_state.timber_in_forest * FOREST_GROWTH_RATE_PER_TURN
    st.session_state.timber_in_forest += growth
    add_log(f"Forest grew by {growth:.2f} units. Total timber: {st.session_state.timber_in_forest:.2f}")

    # Market fluctuation (price and demand)
    price_change = random.uniform(-PRICE_FLUCTUATION_RANGE, PRICE_FLUCTUATION_RANGE)
    st.session_state.product_price = max(5, st.session_state.product_price + price_change) # Price doesn't go below 5
    
    demand_fluctuation = random.uniform(-DEMAND_FLUCTUATION_RANGE_PERCENT, DEMAND_FLUCTUATION_RANGE_PERCENT)
    st.session_state.market_demand = max(50, round(INITIAL_MARKET_DEMAND * (1 + demand_fluctuation))) # Demand doesn't go below 50, resets based on initial

    add_log(f"New market price: ${st.session_state.product_price:.2f}/unit. New market demand: {st.session_state.market_demand} units.")

    # Check win/loss conditions
    if st.session_state.money <= 0 and st.session_state.harvested_timber_inventory <=0 and st.session_state.mill_timber_inventory <=0 and st.session_state.processed_product_inventory <=0 :
        st.session_state.game_over = True
        add_log("Game Over! You've run out of money and resources.")
        st.error("Game Over! You've run out of money and resources.")
    
    if st.session_state.money >= INITIAL_MONEY * 5: # Example win condition: 5x initial money
        st.session_state.win_condition_met = True
        st.session_state.game_over = True
        add_log("Congratulations! You've reached the profit target!")
        st.success("Congratulations! You've reached the profit target!")

    if st.session_state.current_turn > 50: # Example turn limit
        st.session_state.game_over = True
        add_log("Game Over! Time limit reached.")
        st.warning("Game Over! Time limit reached.")


# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="Forest Supply Chain Sim")

# Initialize game state if not already done
if 'current_turn' not in st.session_state:
    initialize_game()

st.title("🌲 Forest Product Supply Chain Simulator 🌲")
st.markdown(f"**Turn: {st.session_state.current_turn}** | **Money: ${st.session_state.money:,.2f}**")

if st.session_state.game_over:
    if st.session_state.win_condition_met:
        st.balloons()
    st.warning("The game has ended. Press 'Restart Game' to play again.")
    if st.button("Restart Game", key="restart_game_over"):
        initialize_game()
        st.rerun()

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Forest Management")
    st.metric("Timber in Forest", f"{st.session_state.timber_in_forest:,.0f} units")
    st.metric("Timber Growth/Turn", f"{st.session_state.timber_in_forest * FOREST_GROWTH_RATE_PER_TURN:,.0f} units")
    
    harvest_amount = st.number_input("Amount to Harvest", min_value=0, max_value=min(MAX_HARVEST_PER_TURN, int(st.session_state.timber_in_forest)), step=10, key="harvest_input", disabled=st.session_state.game_over)
    if st.button("Harvest Timber", disabled=st.session_state.game_over):
        harvest_timber(harvest_amount)
        st.rerun()

    st.markdown("---")
    st.metric("Harvested Timber (at Forest)", f"{st.session_state.harvested_timber_inventory:,.0f} units")
    transport_amount = st.number_input("Amount to Transport to Mill", min_value=0, max_value=int(st.session_state.harvested_timber_inventory), step=10, key="transport_input", disabled=st.session_state.game_over)
    if st.button("Transport to Mill", disabled=st.session_state.game_over):
        transport_timber_to_mill(transport_amount)
        st.rerun()


with col2:
    st.header("Mill Operations")
    st.metric("Timber at Mill", f"{st.session_state.mill_timber_inventory:,.0f} units")
    st.metric("Mill Processing Capacity/Turn", f"{MILL_CAPACITY_PER_TURN} units")
    st.metric("Processing Cost/Unit Timber", f"${PROCESSING_COST_PER_UNIT_TIMBER}")

    process_amount = st.number_input("Amount of Timber to Process", min_value=0, max_value=min(MILL_CAPACITY_PER_TURN, int(st.session_state.mill_timber_inventory)), step=10, key="process_input", disabled=st.session_state.game_over)
    if st.button("Process Timber", disabled=st.session_state.game_over):
        process_timber(process_amount)
        st.rerun()
    
    st.markdown("---")
    st.metric("Processed Product Inventory", f"{st.session_state.processed_product_inventory:,.2f} units")


with col3:
    st.header("Market & Sales")
    st.metric("Current Product Price", f"${st.session_state.product_price:,.2f} /unit")
    st.metric("Market Demand this Turn", f"{st.session_state.market_demand:,.0f} units")

    sell_amount = st.number_input("Amount of Product to Sell", min_value=0.0, max_value=float(st.session_state.processed_product_inventory), step=10.0, format="%.2f", key="sell_input", disabled=st.session_state.game_over)
    if st.button("Sell Product", disabled=st.session_state.game_over):
        sell_product(sell_amount)
        st.rerun()

st.markdown("---")

# Next Turn Button - Centered
button_col1, button_col2, button_col3 = st.columns([2,1,2])
with button_col2:
    if st.button("➡️ Advance to Next Turn", type="primary", use_container_width=True, disabled=st.session_state.game_over):
        next_turn()
        st.rerun()

st.markdown("---")
st.header("Game Log")
log_container = st.container(height=200)
for log_entry in st.session_state.logs:
    log_container.text(log_entry)

st.sidebar.header("Game Info & Controls")
st.sidebar.markdown(f"""
**Current Turn:** {st.session_state.current_turn}
**Money:** ${st.session_state.money:,.2f}
**Timber in Forest:** {st.session_state.timber_in_forest:,.0f}
**Harvested Timber (Forest):** {st.session_state.harvested_timber_inventory:,.0f}
**Timber at Mill:** {st.session_state.mill_timber_inventory:,.0f}
**Processed Product:** {st.session_state.processed_product_inventory:,.2f}
**Product Price:** ${st.session_state.product_price:,.2f}
**Market Demand:** {st.session_state.market_demand:,.0f} units
""")

if st.sidebar.button("Restart Game", key="restart_sidebar"):
    initialize_game()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Game Rules & Costs:")
st.sidebar.markdown(f"""
- **Initial Money:** ${INITIAL_MONEY:,.0f}
- **Forest Growth/Turn:** {FOREST_GROWTH_RATE_PER_TURN*100:.1f}%
- **Max Harvest/Turn:** {MAX_HARVEST_PER_TURN} units
- **Harvest Cost:** ${HARVEST_COST_PER_UNIT}/unit
- **Transport Cost:** ${TRANSPORT_COST_PER_UNIT_TIMBER}/unit timber
- **Mill Capacity/Turn:** {MILL_CAPACITY_PER_TURN} units timber
- **Processing Cost:** ${PROCESSING_COST_PER_UNIT_TIMBER}/unit timber
- **Timber to Product Ratio:** {TIMBER_TO_PRODUCT_RATIO} (e.g., 1 timber -> {TIMBER_TO_PRODUCT_RATIO} product)
- **Win Condition:** Reach ${INITIAL_MONEY * 5:,.0f}
- **Lose Condition:** Run out of money and all inventories, or reach Turn 51.
""")
