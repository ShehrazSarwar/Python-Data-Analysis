import streamlit as st
import pandas as pd

st.header('Working with DataFrame')

st.subheader('DataFrame Example')
df = pd.DataFrame({
    "Name": ["Ali", "Sara", "Hassan", "Zara"],
    "Age": [25, 28, 22, 30],
    "City": ["Karachi", "Lahore", "Islamabad", "Quetta"],
    "Score": [88, 92, 79, 85]
})

st.dataframe(df)

# Editable DataFrame
st.subheader('Data Editor')
editable_df = st.data_editor(df)

# Static Table
st.subheader('Static Table')
st.table(df)

# Metrics
st.subheader('Metrics')
st.metric(label='No of Rows:',value=len(df))
st.metric(label='Avg Score:',value= round(df['Score'].mean(),2))

st.divider()

# JSON & Dict
st.subheader('JSON & Dict')
data_json = {
  "name": "Sheeraz Sarwar",
  "age": 25,
  "is_student": False,
  "skills": ["Python", "SQL", "Power BI"],
  "education": {
    "degree": "BS Computer Science",
    "university": "IQRA University",
    "year": 2024
  },
  "projects": [
    {
      "title": "Bookstore Management System",
      "language": "Java",
      "status": "Completed"
    },
    {
      "title": "Data Analysis Dashboard",
      "language": "Python",
      "status": "In Progress"
    }
  ]
}

st.json(data_json)

sample_data = {
    "name": "Sheeraz Sarwar",
    "age": 25,
    "is_student": False,
    "skills": ["Python", "SQL", "Power BI"],
    "education": {
    "degree": "BS Computer Science",
    "university": "IQRA University",
    "year": 2024
  }
}
st.write("Dictionary View",sample_data)
