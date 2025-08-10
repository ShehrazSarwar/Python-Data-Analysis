import streamlit as st
import datetime as dt

info = {
    'Name': None,
    'Age': None,
    'Gender': None,
    'DOB': None
}

max_date = dt.datetime.now()
min_date = dt.datetime(2000,1,1)

st.header('Simple Form')
with st.form('Basic Form'):
    info['Name'] = st.text_input('Enter your name: ')
    info['Age'] = st.number_input('Enter your age: ')
    info['Gender'] = st.selectbox('Gender: ',['Male','Female'])
    info['DOB'] = st.date_input('Select Date of Birth: ',max_value= max_date, min_value= min_date)

    submission_status = st.form_submit_button(label='Submit')
    if submission_status:
        if not all (info.values()):
            st.warning('Please fill all the values!')
        else:
            st.success('Form submitted successfully!')
            st.balloons()
            with st.expander(label='Check Submitted Info:'):
                for key,values in info.items():
                    st.write(f"{key}: {values}")

