CREATE TABLE video_detail (
    video_id varchar(11) CONSTRAINT pk_video_detail PRIMARY KEY,
    title varchar(100) NOT NULL,
    description varchar(2000) NOT NULL,
    thumbnail_url varchar(100) NOT NULL,
    upload_dtm timestamp with time zone NOT NULL,
    length interval NOT NULL,
    movie_type varchar(5) NOT NULL,
    size_high integer NOT NULL,
    size_low integer NOT NULL,
    last_res_body varchar(400),
    watch_url varchar(50) NOT NULL,
    thumb_type varchar(10) NOT NULL,
    embeddable boolean NOT NULL,
    no_live_play boolean NOT NULL,
    genre varchar(20) NOT NULL,
    author_id varchar(11) NOT NULL,
    author_name varchar(50) NOT NULL,
    author_icon_url varchar(100) NOT NULL
);

CREATE TABLE video_stat (
    reg_dtm timestamp with time zone,
    video_id varchar(11),
    num_views integer NOT NULL,
    num_comments integer NOT NULL,
    num_likes integer NOT NULL,
    num_mylists integer NOT NULL,
    CONSTRAINT pk_video_stat PRIMARY KEY (reg_dtm, video_id),
    CONSTRAINT fk_video_detail FOREIGN KEY (video_id) REFERENCES video_detail(video_id)
);

CREATE TABLE video_stat_sandbox (
    reg_dtm timestamp with time zone,
    video_id varchar(11),
    num_views integer NOT NULL,
    num_comments integer NOT NULL,
    num_likes integer NOT NULL,
    num_mylists integer NOT NULL,
    CONSTRAINT pk_video_stat_sandbox PRIMARY KEY (reg_dtm, video_id),
    CONSTRAINT fk_video_detail FOREIGN KEY (video_id) REFERENCES video_detail(video_id)
);

CREATE TABLE video_tag (
    video_id varchar(11),
    tag varchar(50) NOT NULL,
    CONSTRAINT fk_video_detail FOREIGN KEY (video_id) REFERENCES video_detail(video_id)
);
