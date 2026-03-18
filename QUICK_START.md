# Quick Start Guide - Live Test Data Dashboard

## See Live Updates in 3 Steps!

### Step 1: Start the Test Data Generator

Open a terminal and run:
```bash
python populate_test_data.py
```

This will start adding test sensor readings to the database every 5 seconds.

**Options:**
- `--interval 5` - Change update interval (default: 5 seconds)
- `--readings 100` - Generate 100 readings then stop
- `--duration 300` - Run for 5 minutes then stop

**Example:**
```bash
# Update every 3 seconds
python populate_test_data.py --interval 3

# Generate 50 readings then stop
python populate_test_data.py --readings 50
```

### Step 2: Start the Dashboard

Open another terminal and run:
```bash
streamlit run water_quality_dashboard.py
```

### Step 3: Configure Dashboard

1. **Enable Database Storage** - Check the checkbox in sidebar
2. **Select Data Source** - Choose "Database (Latest)"
3. **Set Update Interval** - Set to 5 seconds (or match your generator interval)
4. **Watch it update!** - The dashboard will refresh automatically showing new values

## What You'll See

- **Live Metrics**: pH, Temperature, TDS, and Turbidity updating every 5 seconds
- **Real-time Charts**: Watch the graphs update as new data arrives
- **Database Stats**: See total readings, averages, and date ranges
- **Historical Data**: View past readings from the database

## Test Data Characteristics

The test data generator creates realistic sensor readings with:
- **pH**: Varies between 6.5-7.5 (normal range)
- **Temperature**: 20-25°C with time-based variations
- **TDS**: 250-350 ppm with gradual increases
- **Turbidity**: 1.5-2.5 NTU with random variations

All values change naturally over time to simulate real sensor behavior!

## Troubleshooting

**No data appearing?**
- Make sure `populate_test_data.py` is running
- Check that database is enabled in dashboard sidebar
- Verify "Database (Latest)" is selected as data source

**Values not changing?**
- Ensure update interval matches generator interval
- Check that database path is the same in both scripts
- Look for errors in the terminal running the generator

**Want to stop?**
- Press `Ctrl+C` in the terminal running `populate_test_data.py`
- The dashboard will continue showing the last values

## Next Steps

- Connect real sensors by selecting "Live Sensors" as data source
- Export historical data as CSV
- Adjust test values using the sliders in Test Mode
- View historical trends using the database viewer
