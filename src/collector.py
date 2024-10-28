from logger import get_custom_logger
from db_config import get_db_connection

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz


PAGE_LIMIT = 156

def insert_into_detail(video_id, title, description, thumbnail_url, upload_dtm, length, movie_type,
                     size_high, size_low, last_res_body, watch_url, thumb_type, embeddable,
                     no_live_play, genre, author_id, author_name, author_icon_url):
    return f"""INSERT INTO video_detail (
    video_id,
    title,
    description,
    thumbnail_url,
    upload_dtm,
    length,
    movie_type,
    size_high,
    size_low,
    last_res_body,
    watch_url,
    thumb_type,
    embeddable,
    no_live_play,
    genre,
    author_id,
    author_name,
    author_icon_url)
    VALUES (
    '{video_id}',
    '{title.replace('\'', '\'\'')}',
    '{description.replace('\'', '\'\'')}',
    '{thumbnail_url}',
    '{upload_dtm}',
    '{length}',
    '{movie_type}',
    {int(size_high)},
    {int(size_low)},
    '{None if last_res_body is None else last_res_body.replace('\'', '\'\'')}',
    '{watch_url}',
    '{thumb_type}',
    '{True if int(embeddable) == 1 else False}',
    '{True if int(no_live_play) == 1 else False}',
    '{genre}',
    '{author_id}',
    '{author_name}',
    '{author_icon_url}'
    );"""


def insert_into_tag(video_id, tags):
    queries = []
    for tag in tags:
        queries.append(f"""INSERT INTO video_tag (video_id, tag)
                       VALUES ('{video_id}', '{tag.replace('\'', '\'\'')}');""")
    return "\n".join(queries)


def insert_into_stat(mode, reg_dtm, video_id, num_views, num_comments, num_likes, num_mylists):
    # mode: Trueならdebug, Falseならrelease
    table = "video_stat_sandbox" if mode else "video_stat"
    return f"""INSERT INTO {table} (reg_dtm, video_id, num_views, num_comments, num_likes, num_mylists)
    VALUES ('{reg_dtm}', '{video_id}', {int(num_views)}, {int(num_comments)}, {int(num_likes)}, {int(num_mylists)});"""


def main():
    timezone = pytz.timezone('Asia/Tokyo')
    current_time = datetime.now(timezone)
    logger = get_custom_logger()

    # PostgreSQLに接続
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        logger.info("Successfully connected to the DB.")

    except Exception as e:
        logger.error("Failed to connected to the DB.")
        raise

    # VOCALOIDタグがついた動画を上限件数取得
    for offset in range(PAGE_LIMIT):
        page_url = f"https://www.nicovideo.jp/tag/VOCALOID?page={offset+1}&sort=v&order=d"
        response = requests.get(page_url)

        # ステータスコードが200以外の場合（失敗）は以降の処理をスキップし次のループへ
        if response.status_code != 200:
            logger.warning(f"The request ({page_url}) was failed with status-code: {response.status_code}\n")
            continue

        # HTMLからvideo_idを抽出
        soup = BeautifulSoup(response.text, "lxml")
        video_elems = soup.find_all("li", attrs={"class": "item", "data-video-item": True})
        video_ids = [x["data-video-id"] for x in video_elems]

        for i in range(len(video_ids)):
            # video_idがテーブルvideo_detailに保存されていない場合、新たに追加
            cur.execute(f"SELECT EXISTS (SELECT 1 FROM video_detail WHERE video_id = '{video_ids[i]}');")
            if not cur.fetchone()[0]:
                video_detail_url = f"https://ext.nicovideo.jp/api/getthumbinfo/{video_ids[i]}"
                response = requests.get(video_detail_url)

                # ステータスコードが200以外の場合（失敗）は以降の処理をスキップし次のループへ
                if response.status_code != 200:
                    logger.warning(f"The request ({video_detail_url}) was failed with status-code: {response.status_code}\n")
                    continue

                soup = BeautifulSoup(response.text, features="xml")
                author_id = "c" + soup.ch_id.string if soup.user_id is None else "u" + soup.user_id.string
                author_name = soup.ch_name.string if soup.user_nickname is None else soup.user_nickname.string
                author_icon_url = soup.ch_icon_url.string if soup.user_icon_url is None else soup.user_icon_url.string

                cur.execute(insert_into_detail(video_ids[i], soup.title.string, soup.description.string,
                                               soup.thumbnail_url.string, soup.first_retrieve.string, soup.length.string,
                                               soup.movie_type.string, soup.size_high.string, soup.size_low.string,
                                               soup.last_res_body.string, soup.watch_url.string,
                                               soup.thumb_type.string, soup.embeddable.string,
                                               soup.no_live_play.string, soup.genre.string, author_id, author_name,
                                               author_icon_url
                                               ))
                conn.commit()

                cur.execute(insert_into_tag(video_ids[i], [x.string for x in soup.find_all("tag")]))
                conn.commit()

            # 再生回数等のデータをvideo_statに追加
            cur.execute(insert_into_stat(False, current_time, video_ids[i],
                                         video_elems[i].find("li", {"class": "count view"}).span.text.replace(",", ""),
                                         video_elems[i].find("li", {"class": "count comment"}).span.text.replace(",", ""),
                                         video_elems[i].find("li", {"class": "count like"}).span.text.replace(",", ""),
                                         video_elems[i].find("li", {"class": "count mylist"}).span.text.replace(",", ""),
                                         ))
            conn.commit()
    conn.close()
    logger.info("All done.")


if __name__ == "__main__":
    main()
