import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# 1. 설정 및 API 키 (필수 규칙 준수)
try:
    API_KEY = st.secrets["WEATHER_API_KEY"]
except KeyError:
    st.error("API 키가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인하세요.")
    st.stop()
    
BASE_URL = "http://api.weatherapi.com/v1/forecast.json"

st.set_page_config(page_title="글로벌 날씨 앱", page_icon="🌤️", layout="centered")

# --- CSS 스타일 (네모 칸 디자인) ---
st.markdown("""
    <style>
    /* 강수량 박스 (하늘색) */
    .precip-container {
        background-color: #00BFFF; 
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
    }
    /* 바람세기 박스 (연한 하늘색) */
    .wind-container {
        background-color: #E0F7FA;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: #01579B;
        margin-bottom: 10px;
        border: 1px solid #B2EBF2;
    }
    .metric-label { font-size: 16px; font-weight: bold; margin-bottom: 5px; }
    .metric-value { font-size: 28px; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌏 실시간 기상 관측소")

# --- 위치 설정 로직 ---
st.subheader("📍 위치 설정")
loc = get_geolocation() # GPS 시도

# 1. 드롭다운 리스트에 GPS 옵션을 명시적으로 추가합니다.
city_list = ["📍 내 위치 (GPS)", "서울", "부산", "제주", "인천", "대구", "대전", "광주", "직접 입력"]
selected_city = st.selectbox("조회할 지역을 선택하세요", options=city_list)

query = None

# 2. 사용자가 드롭다운에서 무엇을 선택했는지에 따라 명확히 분기합니다.
if selected_city == "📍 내 위치 (GPS)":
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        query = f"{lat},{lon}"
        st.success(f"✅ GPS 위치 확인: {lat:.2f}, {lon:.2f}")
    else:
        st.info("GPS 권한을 허용하거나 위치 정보를 가져오는 중입니다...")
else:
    city_map = {
        "서울": "Seoul", "부산": "Busan", "제주": "Jeju", 
        "인천": "Incheon", "대구": "Daegu", "대전": "Daejeon", "광주": "Gwangju"
    }
    
    if selected_city == "직접 입력":
        query = st.text_input("도시 이름을 영어로 입력하세요", "London")
    else:
        query = city_map[selected_city]

# --- 데이터 로드 ---
if query:
    params = {"key": API_KEY, "q": query, "days": 1, "lang": "ko"}
    
    try:
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            res = response.json()
            
            loc_data = res['location']
            curr = res['current']
            forecast = res['forecast']['forecastday'][0]['day']
            astro = res['forecast']['forecastday'][0]['astro']
            
            temp = curr['temp_c']
            cond = curr['condition']['text']
            wind = curr['wind_kph']
            precip = curr['precip_mm']

            # 1. 메인 날씨 카드
            st.markdown(f"""
                <div style="background-color:#3498db; padding:25px; border-radius:20px; text-align:center; color:white; margin-bottom:20px;">
                    <h2 style="margin:0;">{loc_data['name']}</h2>
                    <h1 style="font-size: 50px; margin:10px 0;">🌡️ {temp}°C</h1>
                    <h3 style="margin:0;">{cond}</h3>
                </div>
            """, unsafe_allow_html=True)

            # 2. [핵심] 강수량 및 바람세기 (오늘 밤 달 형태의 네모칸)
            # 옷차림 추천 바로 위에 위치
            col_p, col_w = st.columns(2)
            
            with col_p:
                p_emoji = "🌧️" if "비" in cond else "⛄" if "눈" in cond else "💧"
                st.markdown(f"""
                    <div class="precip-container">
                        <div class="metric-label">{p_emoji} 강수량</div>
                        <div class="metric-value">{precip} mm</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_w:
                st.markdown(f"""
                    <div class="wind-container">
                        <div class="metric-label">💨 바람 세기</div>
                        <div class="metric-value">{wind} km/h</div>
                    </div>
                """, unsafe_allow_html=True)

            # 3. 추천 옷차림
            st.subheader("👔 추천 옷차림")
            if temp >= 25: outfit = "👕 시원한 반팔과 반바지"
            elif temp >= 15: outfit = "🧥 가벼운 가디건이나 셔츠"
            elif temp >= 5: outfit = "🧥 코트나 두꺼운 외투"
            else: outfit = "🧣 패딩과 방한용품 필수"
            
            if precip > 0:
                outfit += " (🌂 우산이나 장화 필수!)"
            st.info(outfit)

            # 4. 기타 정보 (st.metric 형태 유지)
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("💦 습도", f"{curr['humidity']}%")
            c2.metric("🤒 체감", f"{curr['feelslike_c']}°C")
            
            moon_map = {
                "New Moon": "🌑 신월", "Full Moon": "🌕 보름달", 
                "First Quarter": "🌓 상현달", "Last Quarter": "🌗 하현달",
                "Waxing Crescent": "🌒 초승달", "Waxing Gibbous": "🌔 차오르는 달",
                "Waning Gibbous": "🌖 기우는 달", "Waning Crescent": "🌘 그믐달"
            }
            c3.metric("🌙 오늘 밤 달", moon_map.get(astro['moon_phase'], "🌙 확인중"))
            
            st.caption(f"최종 업데이트: {loc_data['localtime']}")
            
        else:
            st.error("날씨 데이터를 불러오는데 실패했습니다. 입력하신 도시 이름을 확인해주세요.")
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")

else:
    st.info("지역을 선택하거나 GPS 권한을 허용해 주세요.")