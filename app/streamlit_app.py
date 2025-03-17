from util.logger import get_custom_logger
from util.db_config import get_db_connection
from util.extract import get_normal_stat, get_period_stat, display_stat

import streamlit as st
import pytz
from datetime import datetime


def total_views():
    st.write(f"総再生回数ランキング ({st.session_state.df['reg_dtm'].max().astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M')}時点)")
    display_stat("num_views")


def total_comments():
    st.write(f"総コメント数ランキング ({st.session_state.df['reg_dtm'].max().astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M')}時点)")
    display_stat("num_comments")


def total_likes():
    st.write(f"総いいね数ランキング ({st.session_state.df['reg_dtm'].max().astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M')}時点)")
    display_stat("num_likes")


def total_mylists():
    st.write(f"マイリスト登録数ランキング ({st.session_state.df['reg_dtm'].max().astimezone(pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M')}時点)")
    display_stat("num_mylists")


def video_detail():
    st.write("Hello")


# Streamlitアプリのタイトル
st.title('VOCALYZE')

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.is_normal = False
    st.session_state.agg_period = None
    # 初回起動時に実行するコード
    st.write("アプリが起動しました！初回のみ表示されるメッセージです。")

    st.session_state.logger = get_custom_logger()
    # PostgreSQLに接続
    try:
        st.session_state.conn = get_db_connection()
        st.session_state.logger.info("Successfully connected to the DB.")

    except Exception as e:
        st.session_state.logger.error("Failed to connected to the DB.")
        raise

st.session_state.trend_mode = st.checkbox("現在の流行曲に並べ替え")

if st.session_state.trend_mode:
    agg_period = st.selectbox("集計期間", ("月間","週間","日間","1時間"))
    if st.session_state.is_normal or agg_period != st.session_state.agg_period:
        st.session_state.is_normal = False
        st.session_state.agg_period = agg_period
        st.session_state.df = get_period_stat(agg_period)
        st.session_state.artists = st.session_state.df["author_name"].unique()
        print("period_stat")
elif not st.session_state.trend_mode and not st.session_state.is_normal:
    st.session_state.is_normal = True
    st.session_state.df = get_normal_stat()
    st.session_state.artists = st.session_state.df["author_name"].unique()
    print("normal_stat")

st.session_state.year = st.selectbox(label="リリース年を選ぶ", options=range(2007,datetime.now().year+1), index=None)
st.session_state.artist = st.selectbox(label="アーティストを指定する", options=st.session_state.artists, index=None)
st.session_state.offset = st.number_input("OFFSET:", min_value=0, value=0, step=100)

pg = st.navigation([st.Page(total_views), st.Page(total_comments),st.Page(total_likes), st.Page(total_mylists)])
pg.run()

# アプリを終了するためのボタン
if st.button("アプリを終了する"):
    # アプリ終了時に実行したい処理
    st.session_state.my_variable = "アプリが終了しました！"
    st.write(st.session_state.my_variable)
    st.session_state.conn.close()

    # 一時的にセッションをリセット
    st.session_state.clear()  # セッションステートをクリア
