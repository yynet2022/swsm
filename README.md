# swsm
Simple Work Schedule Management (django)  
Djangoによる勤務予定表です。

## Features （特徴）
- ユーザの予定入力は日毎、月一括などが可能。
- 終日休、AM休、PM休の休暇入力対応。
- 終日出社、部分在宅、終日在宅の勤務形態入力対応。
- 勤務開始、勤務中断、勤務再開、勤務終了の現状入力およびログ確認。
- お気に入りユーザの勤務状態確認。
- 他ユーザの予定を参照。
- 管理者により休日および連絡事項登録。
- 独自のメール認証。
- ready to use, nice user interface.

## Sample
![勤務予定表_20220108_00](https://user-images.githubusercontent.com/97294053/148630638-645ba1fc-d823-435f-97b8-d4c4a2d092c3.png)

## Requirements
* Python 3.9.2
* Django 3.2.9
* uWSGI 2.0.20 (optional)
* Google Chrome

Currently only tested against Python 3.9.2, Django 3.2.9 and Google Chrome.
It may be supported by other versions and browsers.

## Installation
```bash
pip install Django
pip install uWSGI
```

```bash
git clone https://github.com/yynet2022/swsm.git
cd swsm
python manage.py easy_setup 
```

Edit `project/local_settings.py`

Check `ALLOWED_HOSTS`, `DEFAULT_FROM_EMAIL`, and `EMAIL_HOST`

Edit `uwsgi.ini`

Check `http=0:8000`

```bash
python manage.py runserver 0:8000
```
or
 
```bash
uwsgi uwsgi.ini 
```

## License
This is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).


Thank you!
