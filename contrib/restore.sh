#! /bin/sh

D=${1:-"_Not_exist_directory."}
test -d "$D" || exit 1

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
    python manage.py "$c" -v 0 -c -f "${D}/${c}.csv" >/dev/null
done

echo "done. ($D)"
