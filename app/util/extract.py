import streamlit as st
import pandas as pd


def get_normal_stat():
    cur = st.session_state.conn.cursor()
    query = f"""
    SELECT *
    FROM (
        SELECT video_id, title, author_name, watch_url, upload_dtm
        FROM video_detail
    ) NATURAL JOIN (
        SELECT *
        FROM video_stat
        WHERE reg_dtm = (SELECT MAX(reg_dtm) FROM video_stat)
    );"""

    cur.execute(query)
    columns = [description[0] for description in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns=columns)

    return df


def get_period_stat(interval):
    cur = st.session_state.conn.cursor()
    cur.execute("SELECT DISTINCT reg_dtm FROM video_stat ORDER BY reg_dtm;")
    reg_dtms = cur.fetchall()
    rough_reg_dtms = [x[0].replace(second=0, microsecond=0) for x in reg_dtms]
    now = rough_reg_dtms[-1]

    if interval == "月間":
        for i in range(len(rough_reg_dtms)-1,-1,-1):
            if rough_reg_dtms[i] <= now - pd.Timedelta(days=30):
                past_index = i
                break
    elif interval == "週間":
        for i in range(len(rough_reg_dtms)-1,-1,-1):
            if rough_reg_dtms[i] <= now - pd.Timedelta(weeks=1):
                past_index = i
                break
    elif interval == "日間":
        for i in range(len(rough_reg_dtms)-1,-1,-1):
            if rough_reg_dtms[i] <= now - pd.Timedelta(days=1):
                past_index = i
                break
    else:
        for i in range(len(rough_reg_dtms)-1,-1,-1):
            if rough_reg_dtms[i] <= now - pd.Timedelta(hours=1):
                past_index = i
                break
    if i == 0: past_index = i

    query = f"""
    SELECT *
    FROM (
        SELECT video_id, title, author_name, watch_url, upload_dtm
        FROM video_detail
    ) NATURAL JOIN (
        SELECT *
        FROM video_stat
        WHERE reg_dtm = '{reg_dtms[-1][0]}'
    );"""
    cur.execute(query)
    columns_0 = [description[0] for description in cur.description]
    new_stat = cur.fetchall()
    cur.execute(f"SELECT * FROM video_stat WHERE reg_dtm = '{reg_dtms[past_index][0]}'")
    columns_1 = [description[0] for description in cur.description]
    old_stat = cur.fetchall()

    df0 = pd.DataFrame(new_stat, columns=columns_0)
    df1 = pd.DataFrame(old_stat, columns=columns_1)
    df = df0.merge(df1.drop(columns="reg_dtm"), on="video_id", how="left")
    df["num_views"] = df["num_views_x"] - df["num_views_y"]
    df["num_comments"] = df["num_comments_x"] - df["num_comments_y"]
    df["num_likes"] = df["num_likes_x"] - df["num_likes_y"]
    df["num_mylists"] = df["num_mylists_x"] - df["num_mylists_y"]
    df = df.drop(columns=["num_views_x", "num_views_y", "num_comments_x", "num_comments_y", "num_likes_x", "num_likes_y", "num_mylists_x", "num_mylists_y"])
    
    return df


def display_stat(axis, offset, year):
    if year is None:
        display_df = st.session_state.df.drop(columns=["reg_dtm","video_id"]).sort_values(by=axis, ascending=False).reset_index(drop=True)
    else:
        display_df = st.session_state.df.drop(columns=["reg_dtm","video_id"])
        display_df = display_df[display_df["upload_dtm"].dt.year==year].sort_values(by=axis, ascending=False).reset_index(drop=True)
    display_df["upload_dtm"] = display_df["upload_dtm"].dt.tz_convert('Asia/Tokyo').dt.tz_localize(None).dt.strftime('%Y/%m/%d %H:%M:%S')
    display_df.index = display_df.index + 1
    st.dataframe(display_df.iloc[offset:offset+100],
                 column_config={
                     "watch_url": st.column_config.LinkColumn(
                        "動画URL",
                        display_text=r"https://www.nicovideo.jp/watch/(.*)"
                     )
                 })

