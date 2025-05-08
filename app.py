import streamlit as st
import random
import pandas as pd
import altair as alt

st.set_page_config(page_title="Lotto Number Predictor", layout="centered")
st.title("Lotto Number Predictor with Exportable Ranges")
st.markdown("""
Predict 5 numbers from 1–50 and a bonus number from 1–20.
This strategy excludes obvious sequences (e.g., 1,2,3,4,5 or constant-step sequences like 3,6,9,12,15),
and visualises each chosen number alongside its custom range on a continuum.
Use the sliders to adjust how many numbers below and above each draw are included in the range, then export all results as CSV.
""" )

# Utility to detect arithmetic sequences
def is_arithmetic_sequence(nums):
    if len(nums) < 2:
        return False
    diffs = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
    return all(d == diffs[0] for d in diffs)

# Generate one lotto combination
def generate_lotto_numbers():
    available = list(range(1, 51))
    chosen = []
    for _ in range(5):
        num = random.choice(available)
        chosen.append(num)
        available.remove(num)

    chosen_sorted = sorted(chosen)
    if chosen_sorted == [1,2,3,4,5] or is_arithmetic_sequence(chosen_sorted):
        return generate_lotto_numbers()

    bonus = random.choice(list(range(1, 21)))
    return chosen_sorted, bonus

# Sidebar controls
num_combos = st.sidebar.slider("Number of combinations", min_value=1, max_value=10, value=1)
lower_offset = st.sidebar.slider("Lower range offset", min_value=0, max_value=10, value=3)
upper_offset = st.sidebar.slider("Upper range offset", min_value=0, max_value=10, value=3)

if st.button("Generate Lotto Numbers"):
    export_data = []
    for idx in range(1, num_combos + 1):
        combo, bonus = generate_lotto_numbers()
        exp = st.expander(f"Combination {idx}")
        with exp:
            st.subheader(f"Numbers: {combo}  •  Bonus: {bonus}")
            st.write(f"Range offsets: {lower_offset} below, {upper_offset} above each number")

            # Compute ranges
            ranges = []
            for n in combo:
                start = max(1, n - lower_offset)
                end = min(49, n + upper_offset)
                ranges.append({"Number": n, "Start": start, "End": end})

            range_df = pd.DataFrame(ranges)
            st.write("**Number Ranges**")
            st.table(range_df)

            # Visualization
            rule = alt.Chart(range_df).mark_rule(color='gray', size=4).encode(
                x='Start:Q',
                x2='End:Q'
            )
            circles = alt.Chart(range_df).mark_circle(size=100).encode(
                x='Number:Q',
                tooltip=['Number', 'Start', 'End']
            )
            chart = alt.layer(rule, circles).properties(
                width=600,
                height=100,
                title='Number Ranges Continuum'
            )
            st.altair_chart(chart, use_container_width=True)

        # Prepare export record
        record = {}
        for i, n in enumerate(combo, start=1):
            record[f"Num{i}"] = n
            record[f"Low{i}"] = max(1, n - lower_offset)
            record[f"High{i}"] = min(49, n + upper_offset)
        record["Bonus"] = bonus
        export_data.append(record)

    # Export button
    df_export = pd.DataFrame(export_data)
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Export combos as CSV",
        data=csv,
        file_name="lotto_combinations.csv",
        mime="text/csv"
    )
