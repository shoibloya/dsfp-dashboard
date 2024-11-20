import streamlit as st
import pandas as pd
import plotly.express as px

# Set Streamlit layout to wide and apply a custom theme
st.set_page_config(layout="wide", page_title="Data Engagement Dashboard")

# Load CSV files into dataframes
download_brochure_df = pd.read_csv("Download_Brochure.csv")
gave_feedback_df = pd.read_csv("Gave_Feedback.csv")
signed_up_preview_df = pd.read_csv("Signed_Up_Preview.csv")
attended_preview_df = pd.read_csv("Attended_Preview.csv")

# Title for the app with a subtitle
st.title("📊 DSFP Dashboard")
st.markdown("Use the checkboxes below to filter data and view statistics.")

# Create a sidebar for checkboxes
st.sidebar.header("Filter Options")
download_brochure = st.sidebar.checkbox("Download Brochure", help="Users who downloaded the brochure")
signed_up_for_preview = st.sidebar.checkbox("Signed Up For Preview", help="Users who signed up for a preview")
attended_preview = st.sidebar.checkbox("Attended Preview", help="Users who attended the preview")
gave_feedback = st.sidebar.checkbox("Gave Feedback", help="Users who gave feedback")

# Dictionary to map checkboxes to dataframes
checkbox_to_df = {
    "Download Brochure": download_brochure_df,
    "Signed Up For Preview": signed_up_preview_df,
    "Attended Preview": attended_preview_df,
    "Gave Feedback": gave_feedback_df,
}

# List to track selected dataframes and labels
selected_dfs = []
selected_labels = []

# Iterate over checkboxes and add corresponding dataframes if checked
for label, checkbox in zip(checkbox_to_df.keys(), [download_brochure, signed_up_for_preview, attended_preview, gave_feedback]):
    if checkbox:
        selected_dfs.append(checkbox_to_df[label])
        selected_labels.append(label)

# Function to calculate percentages
def calculate_percentage(part, whole):
    return round((part / whole) * 100, 2) if whole > 0 else 0

# Display results based on selections
if selected_dfs:
    # Get the intersection of 'Email's in all selected dataframes
    emails_intersection = set(selected_dfs[0]['Email'])
    for df in selected_dfs[1:]:
        emails_intersection = emails_intersection.intersection(set(df['Email']))

    # Now, for each selected dataframe, calculate statistics
    stats = []
    for label, df in zip(selected_labels, selected_dfs):
        total_count = df['Email'].nunique()
        intersection_count = df['Email'].isin(emails_intersection).sum()
        outside_count = total_count - intersection_count
        stats.append({
            'Category': label,
            'Total Emails': total_count,
            'Emails in Intersection': intersection_count,
            'Emails not in Intersection': outside_count,
            'Percentage in Intersection': calculate_percentage(intersection_count, total_count),
            'Percentage not in Intersection': calculate_percentage(outside_count, total_count),
        })

    # Convert stats to dataframe
    stats_df = pd.DataFrame(stats)

    # Create tabs for Statistics and Data Table
    tab1, tab2 = st.tabs(["📈 Statistics", "📝 Filtered Data"])

    with tab1:
        st.subheader('Statistics Overview')
        
        st.dataframe(stats_df, use_container_width=True)

        
        # Create a bar chart for Percentage in Intersection
        fig = px.bar(
            stats_df,
            x='Category',
            y='Percentage in Intersection',
            title='Percentage of Emails in Intersection',
            text='Percentage in Intersection',
            labels={'Percentage in Intersection': 'Percentage (%)'}
        )
        fig.update_traces(texttemplate='%{text:.2s}%', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader('Filtered Data Tables')

        # Display the intersection table
        st.markdown("### 👥 Intersection of Selected Categories")
        # Merge all selected dataframes on 'Email' and 'Name' to get the intersection data
        merged_df = selected_dfs[0][selected_dfs[0]['Email'].isin(emails_intersection)].copy()
        for df in selected_dfs[1:]:
            merged_df = pd.merge(merged_df, df, on=['Email', 'Name'], how='inner')
        # Remove duplicate columns if any
        merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
        st.dataframe(merged_df.reset_index(drop=True), use_container_width=True)

        # Now, for each selected category, display the entries not in the intersection
        for label, df in zip(selected_labels, selected_dfs):
            st.markdown(f"### 📄 Entries Unique to **{label}**")
            # Get entries not in the intersection
            unique_df = df[~df['Email'].isin(emails_intersection)].copy()
            if not unique_df.empty:
                st.dataframe(unique_df.reset_index(drop=True), use_container_width=True)
            else:
                st.info(f"All entries in **{label}** are part of the intersection.")

else:
    st.info("Select at least one filter option from the sidebar to display data.")
