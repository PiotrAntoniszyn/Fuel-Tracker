import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client
from typing import List, Dict, Optional
import numpy as np
from auth import SimpleAuth

# Page config for PWA
st.set_page_config(
    page_title="Fuel Tracker",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile optimization
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        border-radius: 0.5rem;
    }
    
    .stNumberInput > div > div > input {
        font-size: 1.1rem;
        height: 3rem;
    }
    
    .stSelectbox > div > div > select {
        font-size: 1.1rem;
        height: 3rem;
    }
    
    .stDateInput > div > div > input {
        font-size: 1.1rem;
        height: 3rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        if not url or not key:
            st.error("Please set SUPABASE_URL and SUPABASE_KEY in your secrets.toml file")
            st.stop()
        return create_client(url, key)
    except KeyError as e:
        st.error(f"Missing secret: {e}. Please add SUPABASE_URL and SUPABASE_KEY to secrets.toml")
        st.stop()
    except Exception as e:
        st.error(f"Error loading secrets: {e}")
        st.stop()

supabase: Client = init_supabase()

# Initialize authentication
@st.cache_resource
def init_auth():
    return SimpleAuth(supabase)

auth = init_auth()

class FuelCalculator:
    @staticmethod
    def calculate_price_per_liter(amount_pln: float, liters: float) -> float:
        """Calculate price per liter"""
        return amount_pln / liters if liters > 0 else 0
    
    @staticmethod
    def find_full_tank_segments(df: pd.DataFrame) -> List[Dict]:
        """Find full-to-full segments for consumption calculation"""
        if df.empty:
            return []
        
        # Sort by timestamp
        df_sorted = df.sort_values('ts').copy()
        full_tanks = df_sorted[df_sorted['is_full_tank'] == True].copy()
        
        segments = []
        for i in range(len(full_tanks) - 1):
            start_row = full_tanks.iloc[i]
            end_row = full_tanks.iloc[i + 1]
            
            # Get all entries between these two full tanks (inclusive of end, exclusive of start)
            segment_entries = df_sorted[
                (df_sorted['ts'] > start_row['ts']) & 
                (df_sorted['ts'] <= end_row['ts'])
            ]
            
            if len(segment_entries) > 0:
                distance = end_row['odometer_km'] - start_row['odometer_km']
                fuel_used = segment_entries['liters'].sum()
                cost_total = segment_entries['amount_pln'].sum()
                
                if distance > 0:
                    consumption = (fuel_used / distance) * 100
                    cost_per_100km = (cost_total / distance) * 100
                    
                    segments.append({
                        'start_date': start_row['ts'],
                        'end_date': end_row['ts'],
                        'distance_km': distance,
                        'fuel_used_l': fuel_used,
                        'cost_total_pln': cost_total,
                        'consumption_l_per_100km': consumption,
                        'cost_per_100km': cost_per_100km,
                        'end_entry_id': end_row['id']
                    })
        
        return segments
    
    @staticmethod
    def calculate_range_accuracy(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate range accuracy for each entry"""
        if df.empty:
            return df
        
        df_sorted = df.sort_values('ts').copy()
        df_sorted['range_accuracy'] = None
        
        for i in range(len(df_sorted) - 1):
            current_row = df_sorted.iloc[i]
            next_row = df_sorted.iloc[i + 1]
            
            predicted_range = current_row['range_after_km']
            actual_distance = next_row['odometer_km'] - current_row['odometer_km']
            
            if predicted_range > 0:
                error_pct = abs(predicted_range - actual_distance) / max(predicted_range, 1) * 100
                accuracy = max(0, min(100, 100 - error_pct))
                df_sorted.iloc[i, df_sorted.columns.get_loc('range_accuracy')] = accuracy
        
        return df_sorted

class FuelDatabase:
    @staticmethod
    def insert_entry(entry_data: Dict) -> bool:
        """Insert a new fuel entry"""
        try:
            result = supabase.table('fuel_entry').insert(entry_data).execute()
            return True
        except Exception as e:
            st.error(f"Error saving entry: {str(e)}")
            return False
    
    @staticmethod
    def get_all_entries() -> pd.DataFrame:
        """Get all fuel entries"""
        try:
            result = supabase.table('fuel_entry').select('*').order('ts', desc=True).execute()
            if result.data:
                df = pd.DataFrame(result.data)
                df['ts'] = pd.to_datetime(df['ts'])
                return df
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading entries: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def validate_entry(liters: float, amount_pln: float, range_before: int, 
                      range_after: int, odometer: int, last_odometer: Optional[int]) -> List[str]:
        """Validate fuel entry data"""
        errors = []
        
        if liters <= 0:
            errors.append("Liters must be greater than 0")
        if amount_pln <= 0:
            errors.append("Amount must be greater than 0")
        if range_before < 0:
            errors.append("Range before cannot be negative")
        if range_after < range_before:
            errors.append("Range after must be >= range before")
        if odometer <= 0:
            errors.append("Odometer must be greater than 0")
        if last_odometer and odometer <= last_odometer:
            errors.append(f"Odometer must be greater than last reading ({last_odometer} km)")
        
        return errors

def quick_add_form():
    """Quick Add fuel entry form"""
    st.header("⛽ Quick Add")
    
    # Get last entry for validation and hints
    df = FuelDatabase.get_all_entries()
    last_entry = df.iloc[0] if not df.empty else None
    last_odometer = last_entry['odometer_km'] if last_entry is not None else None
    
    with st.form("fuel_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            entry_date = st.date_input("Date", value=datetime.now().date())
            entry_time = st.time_input("Time", value=datetime.now().time())
            liters = st.number_input("Liters", min_value=0.01, step=0.01, format="%.2f")
            amount_pln = st.number_input("Amount (PLN)", min_value=0.01, step=0.01, format="%.2f")
        
        with col2:
            range_before = st.number_input("Range before (km)", min_value=0, step=1)
            range_after = st.number_input("Range after (km)", min_value=0, step=1)
            odometer = st.number_input("Odometer (km)", min_value=1, step=1, 
                                     help=f"Last reading: {last_odometer} km" if last_odometer else "")
            is_full_tank = st.checkbox("Full tank", value=True)
        
        submitted = st.form_submit_button("💾 Save Entry", use_container_width=True)
        
        if submitted:
            # Combine date and time
            entry_datetime = datetime.combine(entry_date, entry_time)
            
            # Validate
            errors = FuelDatabase.validate_entry(
                liters, amount_pln, range_before, range_after, odometer, last_odometer
            )
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create entry
                entry_data = {
                    'ts': entry_datetime.isoformat(),
                    'liters': float(liters),
                    'amount_pln': float(amount_pln),
                    'range_before_km': int(range_before),
                    'range_after_km': int(range_after),
                    'odometer_km': int(odometer),
                    'is_full_tank': bool(is_full_tank)
                }
                
                if FuelDatabase.insert_entry(entry_data):
                    st.success("✅ Entry saved successfully!")
                    st.experimental_rerun()

def view_entries():
    """View and filter fuel entries"""
    st.header("📋 Fuel Entries")
    
    df = FuelDatabase.get_all_entries()
    
    if df.empty:
        st.info("No fuel entries yet. Add your first entry using the Quick Add tab!")
        return
    
    # Calculate additional metrics
    df['price_per_liter'] = df.apply(lambda row: FuelCalculator.calculate_price_per_liter(
        row['amount_pln'], row['liters']), axis=1)
    
    # Calculate distances
    df_sorted = df.sort_values('ts')
    df_sorted['distance_from_prev'] = df_sorted['odometer_km'].diff()
    
    # Calculate range accuracy
    df_with_accuracy = FuelCalculator.calculate_range_accuracy(df_sorted)
    
    # Get consumption data
    segments = FuelCalculator.find_full_tank_segments(df)
    consumption_map = {seg['end_entry_id']: seg for seg in segments}
    
    # Add consumption data to dataframe
    df_with_accuracy['consumption_l_per_100km'] = None
    df_with_accuracy['cost_per_100km'] = None
    
    for idx, row in df_with_accuracy.iterrows():
        if row['id'] in consumption_map:
            seg = consumption_map[row['id']]
            df_with_accuracy.at[idx, 'consumption_l_per_100km'] = seg['consumption_l_per_100km']
            df_with_accuracy.at[idx, 'cost_per_100km'] = seg['cost_per_100km']
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        show_full_only = st.checkbox("Show only full tank entries")
    with col2:
        date_range = st.date_input("Date range", value=[])
    
    # Apply filters
    display_df = df_with_accuracy.copy()
    if show_full_only:
        display_df = display_df[display_df['is_full_tank'] == True]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        display_df = display_df[
            (display_df['ts'].dt.date >= start_date) & 
            (display_df['ts'].dt.date <= end_date)
        ]
    
    # Display table
    if not display_df.empty:
        # Format display columns
        display_columns = {
            'ts': 'Date',
            'liters': 'Liters',
            'amount_pln': 'Amount (PLN)',
            'price_per_liter': 'Price/L',
            'odometer_km': 'Odometer',
            'distance_from_prev': 'Distance',
            'consumption_l_per_100km': 'L/100km',
            'cost_per_100km': 'Cost/100km',
            'range_before_km': 'Range Before',
            'range_after_km': 'Range After',
            'range_accuracy': 'Accuracy %',
            'is_full_tank': 'Full Tank'
        }
        
        # Format dataframe for display
        display_data = display_df[list(display_columns.keys())].copy()
        display_data.columns = list(display_columns.values())
        
        # Format numeric columns
        numeric_format = {
            'Liters': '{:.2f}',
            'Amount (PLN)': '{:.2f}',
            'Price/L': '{:.2f}',
            'L/100km': '{:.2f}',
            'Cost/100km': '{:.2f}',
            'Accuracy %': '{:.1f}'
        }
        
        for col, fmt in numeric_format.items():
            if col in display_data.columns:
                display_data[col] = display_data[col].apply(
                    lambda x: fmt.format(x) if pd.notna(x) else '-'
                )
        
        # Format date
        display_data['Date'] = display_data['Date'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(display_data, use_container_width=True, hide_index=True)
        
        # Summary statistics
        st.subheader("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_fuel = display_df['liters'].sum()
            st.metric("Total Fuel", f"{total_fuel:.1f} L")
        
        with col2:
            total_cost = display_df['amount_pln'].sum()
            st.metric("Total Cost", f"{total_cost:.2f} PLN")
        
        with col3:
            avg_price = display_df['price_per_liter'].mean()
            st.metric("Avg Price/L", f"{avg_price:.2f} PLN")
        
        with col4:
            # Average consumption from segments
            valid_consumption = display_df['consumption_l_per_100km'].dropna()
            if not valid_consumption.empty:
                avg_consumption = valid_consumption.mean()
                st.metric("Avg Consumption", f"{avg_consumption:.2f} L/100km")
            else:
                st.metric("Avg Consumption", "No data")
    else:
        st.info("No entries match the selected filters.")

def analytics():
    """Analytics and charts"""
    st.header("📈 Analytics")
    
    df = FuelDatabase.get_all_entries()
    
    if df.empty:
        st.info("No data for analytics. Add some fuel entries first!")
        return
    
    # Calculate metrics
    df['price_per_liter'] = df.apply(lambda row: FuelCalculator.calculate_price_per_liter(
        row['amount_pln'], row['liters']), axis=1)
    
    df_with_accuracy = FuelCalculator.calculate_range_accuracy(df.sort_values('ts'))
    segments = FuelCalculator.find_full_tank_segments(df)
    
    # Price trend
    st.subheader("💰 Price per Liter Trend")
    if len(df) > 1:
        fig_price = px.line(df.sort_values('ts'), x='ts', y='price_per_liter',
                           title="Price per Liter Over Time",
                           labels={'ts': 'Date', 'price_per_liter': 'Price (PLN/L)'})
        fig_price.update_layout(height=400)
        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("Need at least 2 entries to show trend")
    
    # Consumption trend
    st.subheader("⛽ Consumption Trend (Full-to-Full)")
    if segments:
        segments_df = pd.DataFrame(segments)
        fig_consumption = px.line(segments_df, x='end_date', y='consumption_l_per_100km',
                                 title="Fuel Consumption Over Time",
                                 labels={'end_date': 'Date', 'consumption_l_per_100km': 'L/100km'})
        fig_consumption.update_layout(height=400)
        st.plotly_chart(fig_consumption, use_container_width=True)
        
        # Cost per 100km
        st.subheader("💸 Cost per 100km Trend")
        fig_cost = px.line(segments_df, x='end_date', y='cost_per_100km',
                          title="Cost per 100km Over Time",
                          labels={'end_date': 'Date', 'cost_per_100km': 'Cost (PLN/100km)'})
        fig_cost.update_layout(height=400)
        st.plotly_chart(fig_cost, use_container_width=True)
    else:
        st.info("Need at least 2 full tank entries to calculate consumption")
    
    # Range accuracy
    st.subheader("🎯 Range Prediction Accuracy")
    accuracy_data = df_with_accuracy[df_with_accuracy['range_accuracy'].notna()]
    if not accuracy_data.empty:
        fig_accuracy = px.line(accuracy_data, x='ts', y='range_accuracy',
                              title="Range Prediction Accuracy Over Time",
                              labels={'ts': 'Date', 'range_accuracy': 'Accuracy (%)'})
        fig_accuracy.update_layout(height=400)
        fig_accuracy.add_hline(y=accuracy_data['range_accuracy'].mean(), 
                              line_dash="dash", 
                              annotation_text=f"Average: {accuracy_data['range_accuracy'].mean():.1f}%")
        st.plotly_chart(fig_accuracy, use_container_width=True)
    else:
        st.info("Need at least 2 entries to calculate range accuracy")

def main():
    """Main application"""
    
    # Check if Streamlit secrets are set
    try:
        if not st.secrets.get("SUPABASE_URL") or not st.secrets.get("SUPABASE_KEY"):
            st.error("Please set up your Supabase credentials in the secrets.toml file")
            st.code("""
            # secrets.toml
            SUPABASE_URL="your_supabase_url_here"
            SUPABASE_KEY="your_supabase_anon_key_here"
            """)
            st.stop()
    except Exception as e:
        st.error("Please create a secrets.toml file with your Supabase credentials")
        st.code("""
        # secrets.toml
        SUPABASE_URL="your_supabase_url_here"
        SUPABASE_KEY="your_supabase_anon_key_here"
        """)
        st.stop()
    
    # Require authentication
    auth.require_auth()
    
    # Main app header with logout button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⛽ Fuel Tracker")
    with col2:
        if st.button("🚪 Logout", type="secondary"):
            auth.logout_user()
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["➕ Quick Add", "📋 Entries", "📈 Analytics"])
    
    with tab1:
        quick_add_form()
    
    with tab2:
        view_entries()
    
    with tab3:
        analytics()

if __name__ == "__main__":
    main()