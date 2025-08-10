import streamlit as st
import numpy as np

# sidebar layout
st.sidebar.title('This is the Siderbar')
st.sidebar.write('You can place elements here also like sliders buttons, and text etc')
sidebar_input1 = st.sidebar.slider(label='Example Sidebar: ',min_value=10,max_value=50)
sidebar_input2 = st.sidebar.text_input('Enter anything here: ')

# Tabs layout
tabs = st.tabs(['Tab-1','Tab-2','Tab-3'])

with tabs[0]:
    st.write('Your are in Tab 1')

with tabs[1]:
    st.write('Your are in Tab 2')

with tabs[2]:
    st.write('Your are in Tab 3')
    
# Columns layout
columns = st.columns(3)

with columns[0]:
    st.header('Column 1')
    st.write('Content for Column 1')

with columns[1]:
    st.header('Column 2')
    st.write('Content for Column 2')

with columns[2]:
    st.header('Column 3')
    st.write('Content for Column 3')

# Container
with st.container(border=True):
    st.write("This is inside the container")
    st.bar_chart(np.random.randn(50, 3))

# placeholder
placeholder = st.empty()
placeholder.write('This is an empty placeholder, useful for dynamic content.')

if st.button('Update Placeholder'):
    placeholder.write('The content of this placeholder has been updated.')

# sidebar input handling
if sidebar_input1:
    st.write(f'This is the sidebar slider input: {sidebar_input1}')
    st.write(f'This is the sidebar text input: {sidebar_input2}')

st.divider()
# File Uploading
file = st.file_uploader("This is a File Uploader: ")
if file:
    st.image(file,caption='This is the image you uploaded',width=400)

