# === Basic Steamlit example ===
from arduino.app_bricks.streamlit_ui import st

st.title("Arduino Streamlit UI Example")
st.write("Interact with your Arduino modules using this web interface.")

if st.button("Send Command"):
    st.success("Command sent to Arduino!")

