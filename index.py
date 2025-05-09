import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Set page configuration
st.set_page_config(
    page_title="Project Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("Projects Dashboard")
st.markdown("A simple analysis of project data across different sectors and activities.")

# Load and process data
@st.cache_data
def load_data():
    try:
        # Try to load the file if it exists
        df = pd.read_csv(r'C:\Users\PC\Documents\iit\CW_Practical\DSPL_CW\Sec. 17 Projects in Commercial Operation (Including Expansions) 2018_0.csv', encoding='latin1')
        return df
    except FileNotFoundError:
        # If file doesn't exist, return None
        return None

@st.cache_data
def clean_data(df):
    if df is None:
        return None
        
    # Make a copy to avoid modifying the original
    cleaned_df = df.copy()
    
    # Handle missing values
    for col in cleaned_df.columns:
        if cleaned_df[col].dtype == 'object':
            # Fill missing text fields with 'Unknown'
            cleaned_df[col] = cleaned_df[col].fillna('Unknown')
        else:
            # Fill missing numeric fields with 0
            cleaned_df[col] = cleaned_df[col].fillna(0)
    
    # Standardize sector names
    if 'Sector' in cleaned_df.columns:
        # Convert to title case and strip whitespace
        cleaned_df['Sector'] = cleaned_df['Sector'].str.title().str.strip()
    
    return cleaned_df

# Sidebar for data upload
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Save uploaded file
        df = pd.read_csv(uploaded_file)
        df.to_csv('project_data.csv', index=False)
        st.success("Data uploaded successfully!")
    
    st.markdown("---")
    st.markdown("### Dashboard Navigation")
    page = st.radio(
        "Select a page to view:",
        ["Overview", "Sector Analysis", "Activity Analysis"]
    )

# Load data
df = load_data()

if df is None:
    st.warning("No data available. Please upload a CSV file using the sidebar.")
else:
    # Clean the data
    df = clean_data(df)
    
    # Display selected page
    if page == "Overview":
        st.header("Projects Overview")
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Projects", len(df))
        
        with col2:
            if 'Sector' in df.columns:
                st.metric("Total Sectors", df['Sector'].nunique())
            else:
                st.metric("Total Sectors", "N/A")
        
        with col3:
            if 'Project Activity' in df.columns:
                st.metric("Total Activities", df['Project Activity'].nunique())
            else:
                st.metric("Total Activities", "N/A")
        
        # Show projects by sector
        if 'Sector' in df.columns:
            st.subheader("Projects by Sector")
            
            # Get top 10 sectors
            sector_counts = df['Sector'].value_counts().reset_index()
            sector_counts.columns = ['Sector', 'Count']
            top_sectors = sector_counts.head(10)
            
            # Create bar chart
            fig = px.bar(
                top_sectors,
                x='Sector',
                y='Count',
                title='Top 10 Sectors by Number of Projects',
                color='Sector'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Display sample data
        st.subheader("Sample Data")
        st.dataframe(df.head(10))
    
    elif page == "Sector Analysis":
        st.header("Sector Analysis")
        
        if 'Sector' in df.columns:
            # Create sector selection
            all_sectors = sorted(df['Sector'].unique())
            selected_sectors = st.multiselect(
                "Select sectors to analyze:",
                options=all_sectors,
                default=all_sectors[:5] if len(all_sectors) > 5 else all_sectors
            )
            
            if not selected_sectors:
                st.warning("Please select at least one sector to analyze.")
            else:
                # Filter data based on selection
                filtered_df = df[df['Sector'].isin(selected_sectors)]
                
                # Create visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sector comparison bar chart
                    sector_counts = filtered_df['Sector'].value_counts().reset_index()
                    sector_counts.columns = ['Sector', 'Count']
                    
                    fig = px.bar(
                        sector_counts.sort_values('Count', ascending=False),
                        x='Sector',
                        y='Count',
                        color='Sector',
                        title='Projects by Sector'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Sector pie chart
                    fig = px.pie(
                        sector_counts,
                        values='Count',
                        names='Sector',
                        title='Distribution of Projects by Sector'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Show projects in selected sectors
                st.subheader("Projects in Selected Sectors")
                st.dataframe(filtered_df[['Name of the Project', 'Sector', 'Project Activity']].head(20))
        else:
            st.error("No 'Sector' column found in the data.")
    
    elif page == "Activity Analysis":
        st.header("Activity Analysis")
        
        if 'Project Activity' in df.columns:
            # Word cloud of activities
            st.subheader("Project Activities Word Cloud")
            
            all_activities = ' '.join(df['Project Activity'].dropna().astype(str))
            
            if all_activities.strip():
                wordcloud = WordCloud(
                    width=800, 
                    height=400, 
                    background_color='white',
                    colormap='viridis',
                    max_words=100
                ).generate(all_activities)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            
            # Top activities table
            st.subheader("Top Project Activities")
            
            activity_counts = df['Project Activity'].value_counts().reset_index()
            activity_counts.columns = ['Activity', 'Count']
            activity_counts['Percentage'] = (activity_counts['Count'] / len(df) * 100).round(2)
            
            # Display top 20 activities
            st.dataframe(activity_counts.head(20))
            
            # Activity by sector
            if 'Sector' in df.columns:
                st.subheader("Top Activities by Sector")
                
                # Get top 5 sectors
                top_sectors = df['Sector'].value_counts().head(5).index.tolist()
                
                # Create tabs for each sector
                tabs = st.tabs(top_sectors)
                
                for i, sector in enumerate(top_sectors):
                    with tabs[i]:
                        # Filter data for this sector
                        sector_df = df[df['Sector'] == sector]
                        
                        # Get top activities for this sector
                        sector_activities = sector_df['Project Activity'].value_counts().reset_index()
                        sector_activities.columns = ['Activity', 'Count']
                        
                        # Display top 10 activities for this sector
                        st.dataframe(sector_activities.head(10))
        else:
            st.error("No 'Project Activity' column found in the data.")

# Footer
st.markdown("---")
st.markdown("Dashboard created with Streamlit")