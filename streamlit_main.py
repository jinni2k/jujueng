from modbus_tk import modbus_tcp
import threading
import time
import streamlit as st
import modbus_tk.defines as cst


class ModbusClient:
    def __init__(self, ip, port):
        self.master = modbus_tcp.TcpMaster(host=ip, port=port)
        self.master.set_timeout(5.0)
        self.continuous_read = False
        self.thread = None

    def start_continuous_read(self, cycle, code, quantity_of_x):
        self.continuous_read = True
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.read_data, args=(cycle, code, quantity_of_x), daemon=True)
            self.thread.start()

    def read_data(self, cycle, code, quantity_of_x):
        try:
            while self.continuous_read:
                data = self.master.execute(1, code, 0, quantity_of_x)
                print(f"읽은 데이터 ({quantity_of_x}개): {data}")  # 실제 애플리케이션에서는 적절히 처리 필요
                time.sleep(cycle)
        except Exception as e:
            print(f"에러 발생: {e}")  # 실제 애플리케이션에서는 적절히 처리 필요
        finally:
            self.master.close()

    def stop_continuous_read(self):
        if self.continuous_read:
            self.continuous_read = False
            if self.thread is not None:
                self.thread.join()  # 스레드가 종료될 때까지 기다림
                self.thread = None



class App:
    def __init__(self):
        self.modbus_client = None

    def run(self):
        st.title("Modbus TCP Client")
        self.initialize_session_state()
        self.create_sidebar()
        self.handle_page_navigation()

    def initialize_session_state(self):
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'Home'

    def create_sidebar(self):
        with st.sidebar:
            st.title("메뉴")
            if st.button("홈"):
                st.session_state['current_page'] = 'Home'
            if st.button("설정"):
                st.session_state['current_page'] = 'Settings'

    def handle_page_navigation(self):
        if st.session_state['current_page'] == 'Home':
            st.header("홈 페이지")
            st.write("여기는 홈 페이지입니다.")
        elif st.session_state['current_page'] == 'Settings':
            self.display_settings_page()

    def display_settings_page(self):
        st.header("설정")
        ip_address = st.text_input("IP 주소", "localhost")
        port = st.number_input("포트", min_value=1, max_value=65535, value=502)
        read_cycle = st.number_input("읽기 주기 (초)", min_value=1, value=5)
        function_code = st.selectbox("Function Code", options=[cst.READ_COILS, cst.READ_DISCRETE_INPUTS, cst.READ_HOLDING_REGISTERS, cst.READ_INPUT_REGISTERS], format_func=lambda x: {cst.READ_COILS: "Read Coils", cst.READ_DISCRETE_INPUTS: "Read Discrete Inputs", cst.READ_HOLDING_REGISTERS: "Read Holding Registers", cst.READ_INPUT_REGISTERS: "Read Input Registers"}[x])
        quantity_of_x = st.number_input("읽을 레지스터 수", min_value=1, value=10)
        continuous_read = st.checkbox("연속 읽기", value=False)
        
        if st.button("읽기 시작"):
            self.modbus_client = ModbusClient(ip_address, port)
            self.modbus_client.start_continuous_read(read_cycle, function_code, quantity_of_x)
            st.write("연속 읽기 시작됨.")

        if st.button("읽기 중지"):
            if self.modbus_client:
                self.modbus_client.stop_continuous_read()
                st.success("연속 읽기가 중지되었습니다.")


if __name__ == "__main__":
    app = App()
    app.run()
