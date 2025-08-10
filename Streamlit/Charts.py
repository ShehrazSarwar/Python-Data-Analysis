import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.subheader('Area Chart')
df1 = pd.DataFrame(np.random.randn(20,3),columns=['A','B','C'])
st.area_chart(df1)

st.divider()

st.subheader('Line Chart')
df2 = pd.DataFrame(np.random.randint(1,10,8).reshape(4,2),columns= ['X','Y'])
st.line_chart(df2)

st.divider()

st.subheader('Bar Chart')
df3 = pd.DataFrame({
    'Students': ['Shehraz','Aaraiz','Umer','Hassan'],
    'Scores': [95,89,77,85]
})
st.bar_chart(df3,x='Students',y='Scores',horizontal=True,height=300)

st.divider()

st.subheader('Scatter Chart')
df4 = df = pd.DataFrame({
    "x": np.random.randint(10, 50, 100),
    "y": np.random.randint(10, 50, 100),
})
st.scatter_chart(df4)

st.divider()

# Matplotlib
x = np.linspace(0, 10, 50)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y, label="sin(x)", color="blue")

ax.set_xlabel("X axis")
ax.set_ylabel("Y axis")
ax.set_title("Basic Line Graph - Matplotlib in Streamlit")
ax.legend()

st.pyplot(fig)
