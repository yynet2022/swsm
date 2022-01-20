#! /bin/sh

D=$(date '+%F_%T')
mkdir $D || exit 1

for c in list_user \
	     list_holiday \
	     list_information \
	     list_schedule \
	     list_favoritegroupuser \
	     list_usersetting \
	     list_worknotificationrecipient \
	     list_userlog
do
    echo "$c"
    python manage.py "$c" >"${D}/${c}.csv"
    python manage.py "$c" -f "${D}/${c}.csv" >/dev/null 2>&1
done

echo "done. ($D)"
