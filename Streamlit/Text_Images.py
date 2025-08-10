import streamlit as st

st.title('Text Elements')
st.header('This is header')
st.subheader('This is sub header')
st.markdown('This is **markdown**')
st.markdown('This is _markdown_')
st.caption('This is a caption')

code_example = """
def greet(name):
    print('hello',name)
"""
st.code(code_example,language="python")
st.divider()

st.image('Streamlit/static/_Quote_.jpeg',caption='A Quote',width=500)