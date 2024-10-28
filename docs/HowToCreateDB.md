# How to create db and tables

PostgreSQLを想定

## 手順 (DB側)

1. dbを作成
    * データベースを作成可能な権限のユーザが作成すること
```
$ createdb vocalyze
```

2. 処理内でデータベースを操作するユーザを作成
    * スーパーユーザーのままデータベースを操作するのはなんか危険そうだから
    * 下記コマンドで作成したユーザには何の権限も与えられていない
```
$ psql vocalyze
vocalyze=# CREATE USER ユーザ名 WITH PASSWORD 'パスワード';
```

3. 作成したユーザにDBを利用するための権限を付与
```
vocalyze=# GRANT CREATE ON SCHEMA public TO ユーザ名;
```

## デバッグ
* データベースに関わる全ユーザ・権限の表示: `\du`
* データベース内の全publicテーブルの表示: `\dt`