# Fuel Expense Tracking App

A simple PWA for tracking fuel expenses, consumption, and range accuracy.

## Features

- Quick fuel entry form
- Automatic calculations (price/liter, consumption, cost/100km)
- Range accuracy tracking
- Simple analytics with charts
- Mobile-optimized interface

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Supabase project and run `database_schema.sql`
4. Copy `.env.example` to `.env` and add your Supabase credentials
5. Run the app: `streamlit run app.py`

## Database Setup

1. Create a new project on [Supabase](https://supabase.com)
2. Go to SQL Editor and run the contents of `database_schema.sql`
3. Get your project URL and anon key from Settings > API
4. Add them to your `.env` file

## Usage

- **Quick Add**: Enter fuel data quickly with automatic validations
- **View Entries**: See all fuel entries with calculated metrics
- **Analytics**: View trends for price, consumption, and range accuracy