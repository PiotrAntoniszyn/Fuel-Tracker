# Fuel Tracker - Setup Guide

## Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.8+ installed
- A Supabase account (free at [supabase.com](https://supabase.com))

### 2. Database Setup
1. Create a new project on Supabase
2. Go to **SQL Editor** in your Supabase dashboard
3. Copy and paste the contents of `database_schema.sql`
4. Click **Run** to create the database table

### 3. Get Your Credentials
1. In Supabase, go to **Settings** → **API**
2. Copy your **Project URL** and **anon/public key**

### 4. Environment Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and add your Supabase credentials:
   ```
   SUPABASE_URL=your_project_url_here
   SUPABASE_KEY=your_anon_key_here
   ```

### 5. Install and Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

The app will open in your browser at `http://localhost:8501`

## First Time Usage

1. **Register**: Create your account on the Register tab
2. **Verify Email**: Check your email and verify your account
3. **Login**: Use your credentials to log in
4. **Add First Entry**: Use the Quick Add tab to enter your first fuel entry

## Features Overview

### 📱 Quick Add
- Fast fuel entry form optimized for mobile
- Automatic validations (odometer must increase, etc.)
- Hints based on previous entries

### 📋 Entries List
- View all fuel entries with calculated metrics
- Filter by full tank entries or date range
- See price per liter, consumption, costs, and range accuracy

### 📈 Analytics
- **Price Trend**: Track fuel price changes over time
- **Consumption**: Full-to-full fuel consumption in L/100km
- **Cost Analysis**: Cost per 100km trends
- **Range Accuracy**: How accurate is your car's range prediction?

## Understanding the Calculations

### Full-to-Full Consumption
- Consumption is only calculated between full tank entries
- This ensures accurate measurements by accounting for tank variations
- Formula: `(fuel_used / distance) × 100`

### Range Accuracy
- Compares your car's predicted range vs. actual distance driven
- Formula: `100% - |predicted - actual| / predicted × 100%`
- Helps you understand how reliable your car's range estimates are

### Cost per 100km
- Total cost divided by distance for full-to-full segments
- Useful for budgeting and comparing efficiency

## Mobile Usage (PWA)

The app is optimized for mobile use:
- **Add to Home Screen**: In your mobile browser, use "Add to Home Screen"
- **Offline Ready**: Basic caching for improved performance
- **Touch Optimized**: Large buttons and easy-to-use forms

## Deployment Options

### Streamlit Cloud (Recommended)
1. Push your code to GitHub
2. Connect your repo to [Streamlit Cloud](https://share.streamlit.io)
3. Add your environment variables in the Streamlit Cloud secrets

### Self-Hosted
- Use `streamlit run app.py` on any server
- Set environment variables on your server
- Consider using a reverse proxy (nginx) for production

## Troubleshooting

### "Missing credentials" error
- Check that your `.env` file exists and has the correct values
- Verify your Supabase URL and key are correct

### "Database error"
- Ensure you've run the `database_schema.sql` script
- Check that your Supabase project is active

### "Authentication failed"
- Verify your email after registration
- Check that email confirmation is enabled in Supabase Auth settings

### Mobile issues
- Try adding the app to your home screen for better experience
- Clear browser cache if forms aren't working properly

## Data Privacy

- All data is stored in your personal Supabase database
- The app is designed for single-user usage
- You have full control over your data

## Support

This is an MVP (Minimum Viable Product) designed for personal use. For issues:
1. Check the troubleshooting section
2. Verify your Supabase setup
3. Check browser console for error messages