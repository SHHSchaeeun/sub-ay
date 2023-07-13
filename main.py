import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import extra_streamlit_components as stx
import datetime
import secrets
import string
import pyrebase
import matplotlib.pyplot as plt

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore

# config
firebaseConfig = {
    "apiKey": "AIzaSyAXk08LkIZ_wxV2IfL85wNGgnZf3MMBysE",
    "authDomain": "sub-ay.firebaseapp.com",
    "databaseURL": "https://sub-ay-default-rtdb.firebaseio.com",
    "projectId": "sub-ay",
    "storageBucket": "sub-ay.appspot.com",
    "messagingSenderId": "607441294810",
    "appId": "1:607441294810:web:692f26e4ed9327cc725ce3",
    "measurementId": "G-NTH81Q3VB0"
}



firebase = pyrebase.initialize_app(firebaseConfig)


if not firebase_admin._apps:
    cred = credentials.Certificate('sub-ay-firebase-adminsdk-10hkz-d4f854d5c6.json')
    default_app = firebase_admin.initialize_app(cred)

db = firestore.client()

# 세션 1: 유저명
if 'username' not in st.session_state:
    st.session_state['username'] = ''

def loginusername():
    st.session_state.username = user['users'][0]['localId']

# 세션 2: 문서명
if 'docname' not in st.session_state:
    st.session_state['docname'] = ''

def logindocname():
    docname = db.collection("users").where("username", "==", st.session_state.username).stream()
    for doc in docname:
        st.session_state.docname = doc.id

# 포인트 df 만드는 함수인데 마이페이지랑 랭킹에서 같이 쓰니까 위로 유배시킴
list_dict_user = []
merged_dict_user = {}
docs_user = db.collection('users').stream()
for doc in docs_user:
    dict_user = doc.to_dict()
    list_dict_user.append(dict_user)
    for key in dict_user.keys():
        if key in merged_dict_user:
            merged_dict_user[key].append(dict_user[key])
        else:
            merged_dict_user[key] = [dict_user[key]]
df_user = pd.DataFrame.from_dict(merged_dict_user)
df_user_point = df_user[['point', 'username']]
df_user_point.sort_values(['point'], inplace=True, ascending=False)
df_user_point.rename(columns={'point': '포인트', 'username': '이름'}, inplace=True)
df_user_point.reset_index(drop=True, inplace=True)

# 로그인
if st.session_state['username'] == '':
    choice_selectbox = st.empty()
    choice = choice_selectbox.selectbox('로그인/회원가입', ['로그인', '회원가입'], key='log/reg')
    if st.session_state.username == '':
        if choice == '회원가입':
            email = st.text_input('이메일')
            password = st.text_input('비밀번호', type='password')
            username = st.text_input('닉네임')
            if st.button('계정 만들기'):
                user = auth.create_user(email=email, password=password, uid=username)
                col_users = db.collection("users").document()
                col_users.set({"email": email, "username": username, "point": 0})
                st.success('회원가입이 완료되었습니다. 로그인해주세요.')
                st.balloons()

        if choice == '로그인':
            auth = firebase.auth()
            login_email_container = st.empty()
            login_password_container = st.empty()

            email_login = login_email_container.text_input('이메일')
            password_login = login_password_container.text_input('비밀번호', type='password')

            login_button = st.empty()

            if login_button.button('로그인'):
                try:
                    login = auth.sign_in_with_email_and_password(email_login, password_login)
                    user = auth.get_account_info(login['idToken'])
                    loginusername()
                    logindocname()
                    login_email_container.empty()
                    login_password_container.empty()
                    choice_selectbox.empty()
                    login_button.empty()
                    st.info(st.session_state.username + '님 안녕하세요! 오늘도 설문조사 많이 참여해주세요 :frog: :elephant: :bear:')
                except Exception as e:
                    st.write(e)
                    st.error('로그인 실패!')

else:
    st.info(st.session_state.username + '님 안녕하세요! 오늘도 설문조사 많이 참여해주세요 :frog: :elephant: :bear:')

sb = st.sidebar
sb.image("sub-ay.png")
sb.caption("성화여고 설문조사 플랫폼 by 우물밖코끼리")

# 메뉴
with st.sidebar:
    menu = option_menu("메뉴", ['마이페이지', '설문조사 참여', '설문조사 업로드', '이벤트존', '사이트 정보'],
                       icons=['house', 'check2-square', 'upload', 'gift', 'info-square'],
                       menu_icon="cast",
                       default_index=1,
                       styles={
                           "container": {"background-color": "#fafafa"},
                           "nav-link-selected": {"background-color": "green"},
                       }
                       )

# 마이페이지
if menu == '마이페이지':

    st.header("마이페이지")
    st.divider()

    today = datetime.date.today()
    target_date = datetime.date(2023, 7, 17)
    vacation = target_date - today
    st.success(f":elephant: 방학 D - {vacation.days} :frog:")

    tab1, tab2, tab3 = st.tabs(["회원정보", "회원정보 관리", "설문조사 관리"])

    with tab1:
        if st.session_state.username != '':
            col1, col2 = st.columns([1, 4])

            col1.write("**이름**")
            col1.write("**이메일**")
            col1.write("**내 포인트**")
            col1.write("**포인트 순위**")

            docs = db.collection("users").where("username", "==", st.session_state.username).stream()
            for doc in docs:
                user_info = doc.to_dict()

            col2.write(st.session_state.username)
            col2.write(user_info['email'])
            col2.write(str(user_info['point']))
            filtered_df = df_user_point.loc[df_user_point['이름'] == st.session_state.username]
            point_index = filtered_df.index[0]
            col2.write(f"{point_index+1}위")
        else:
            st.markdown(':frog: 로그인 해주세요!')

    with tab2:
        if st.button("비밀번호 재설정"):
            if st.session_state.username == '':
                st.error("로그인도 안했잖아?!")
            else:
                st.info("개발자에게 연락주세요")
                # email = user_info['email']
                # link = auth.generate_password_reset_link(email, action_code_settings)
                # Construct password reset email from a template embedding the link, and send
                # using a custom SMTP server.
                # auth.send_custom_email(email, link)
                # st.info('비밀번호 재설정 메일이 발송되었습니다.')

    with tab3:
        st.write('survey에서 uploader가 st.session_state.username인 것만 불러온다')
        st.write('데이터프레임으로 만든다')
        st.write('스트림릿 데이터프레임 편집기로 불러온다?')
        st.write('변경사항을 변수로 받아 firebase에 보낸다???')


# 설문조사 참여
elif menu == '설문조사 참여':
    st.header("설문조사 참여")
    st.caption("설문조사에 참여하고 참여코드를 입력해 포인트를 획득하세요",
               help="참여코드는 설문조사 종료 페이지에서 확인할 수 있습니다."
                    ":a 참여코드가 없다면 개발자에게 문의해주세요")
    st.divider()

    st.subheader("포인트 랭킹")

    st.markdown(f':first_place_medal: {df_user_point.iloc[0]["이름"]}({df_user_point.iloc[0]["포인트"]})')
    st.markdown(f':second_place_medal: {df_user_point.iloc[1]["이름"]}({df_user_point.iloc[1]["포인트"]})')
    st.markdown(f':third_place_medal: {df_user_point.iloc[2]["이름"]}({df_user_point.iloc[2]["포인트"]})')
    df_user_point.index = df_user_point.index + 1
    with st.expander("전체 랭킹 보기"):
        st.write(df_user_point)

    st.divider()



    with st.form(key='code', clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        code_submit = col1.text_input("참여코드 입력", label_visibility="collapsed")
        if col2.form_submit_button("참여코드 입력"):
            if code_submit == '':
                st.warning('참여코드를 입력해주세요')
            else:
                doc_sur = db.collection("survey").where('code', "==", code_submit).stream()
                doc_sur_dict = doc_sur.get().to_dict()
                if st.session_state.username == '':
                    col1.warning("로그인해주세요!")
                elif st.session_state.username in doc_sur_dict["submit"]:
                    col1.warning("한번만 참여해주세요!")
                else:
                    db.collection("users").document(st.session_state.docname).update({"point": firestore.Increment(100)})

    list_dict_sur = []
    merged_dict_sur = {}
    docs_sur = db.collection('survey').stream()
    for doc in docs_sur:
        dict_sur = doc.to_dict()
        dict_sur.pop('submit', None)
        list_dict_sur.append(dict_sur)
        for key in dict_sur.keys():
            if key in merged_dict_sur:
                merged_dict_sur[key].append(dict_sur[key])
            else:
                merged_dict_sur[key] = [dict_sur[key]]
    df_sur = pd.DataFrame.from_dict(merged_dict_sur)
    df_sur_show = df_sur[['title', 'link', 'grade', 'date']]
    df_sur_show.rename(columns={'title': '제목',
                                'link': '링크',
                                'grade': '참여대상',
                                'date': '종료날짜'}, inplace=True)
    df_sur_show = df_sur_show[['제목', '링크', '참여대상', '종료날짜']]
    st.write(df_sur_show)

# 설문조사 업로드
elif menu == '설문조사 업로드':

    st.header("설문조사 업로드")
    st.caption("링크를 업로드하고 설문조사를 효과적으로 홍보해보세요. :a 참여코드는 반드시 **설문조사 확인 메시지** 에 기입해주세요.")
    st.divider()
    if st.session_state.username == '':
        st.warning("로그인해주세요!")
    u_title = st.text_input('제목', max_chars=30)
    u_link = st.text_input('링크', max_chars=50)
    u_grade = st.text_input('참여대상', max_chars=12, help='예시: 1학년, 3학년 문과, 전학년 등')
    u_date = st.date_input('종료날짜')
    col1, col2 = st.columns([1, 4])
    option = col1.selectbox('직접입력/랜덤입력', ('직접입력', '랜덤입력'))
    if option == '직접입력':
        u_code = col2.text_input('참여코드', max_chars=10)
    elif option == '랜덤입력':
        alphabet = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(4))
        u_code = col2.text_input('참여코드', value=code, max_chars=10)

    if u_title != '' and u_link != '' and u_grade != '' and u_date != '' and u_code != '':
        if st.session_state.username == '':
            st.warning("로그인이 필요합니다!")
        else:
            if st.button('업로드'):

                sur_check = db.collection("survey").where("code", "==", u_code).stream()
                doc = ''
                for doc in sur_check:
                    code_check = doc

                if doc:
                    st.error('코드가 중복됩니다. 다른 코드를 입력해주세요.')

                else:
                    doc_sur = db.collection("survey").document()
                    doc_sur.set({'title': u_title,
                                 'link': u_link,
                                 'grade': u_grade,
                                 'date': str(u_date),
                                 'code': u_code,
                                 'uploader': st.session_state.username})
                    st.success("업로드가 완료되었습니다. "
                               ":a '설문조사 참여' 메뉴에서 설문조사가 정상적으로 조회되는지 확인해주세요.")

# 이벤트존
elif menu == '이벤트존':
    st.header("이벤트존")
    st.caption("가벼운 투표에 참여하고 포인트를 획득하세요")
    st.divider()

    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 3])

    doc_eve = db.collection("event").document("6y12dOH7AJjBa7uKiZNP")
    doc_eve_dict = doc_eve.get().to_dict()

    col3.markdown("ㅤVS")
    if col2.button("카레"):
        if st.session_state.username == '':
            col1.warning("로그인해주세요!")
        elif st.session_state.username in doc_eve_dict["check"]:
            col1.warning("한번만 참여해주세요!")
        else:
            doc_eve.update({"check": firestore.ArrayUnion([st.session_state.username])})
            doc_eve.update({"former": firestore.Increment(1)})
            db.collection("users").document(st.session_state.docname).update({"point": firestore.Increment(100)})
    if col4.button("짜장"):
        if st.session_state.username == '':
            col5.warning("로그인해주세요!")
        elif st.session_state.username in doc_eve_dict["check"]:
            col5.warning("한번만 참여해주세요!")
        else:
            doc_eve.update({"check": firestore.ArrayUnion([st.session_state.username])})
            doc_eve.update({"latter": firestore.Increment(1)})
            db.collection("users").document(st.session_state.docname).update({"point": firestore.Increment(100)})

    sizes = [doc_eve_dict["former"], doc_eve_dict["latter"]]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, autopct=lambda p: '{:.1f}%'.format(p), colors=['#ffea5e', '#85645b'], radius=1)
    st.pyplot(fig1)

# 사이트 정보
elif menu == '사이트 정보':
    st.header('사이트 정보')
    st.divider()

    st.markdown('**개발진** 김채은(wc2756@naver.com), 서시연, 유민아')

    st.markdown('**Q** 사이트는 어떻게 만들었나요?'
                ':a **A** 파이썬 라이브러리 Streamlit을 통해 제작했습니다. 데이터베이스는 Google firebase를 사용합니다.')

    st.markdown('**Q** 로그인 기능이 있는데, 안심하고 이용해도 되나요?'
                ':a **A** Google firebase에서 제공하는 기능으로, 개발진도 비밀번호에 접근할 수 없습니다.')
