jsonpost1 host-ip/stations-request/
post:
-format=iaf or iaga2002 or add
return:
{'khb': [[1577826000, 1606770000]], 'mgd': [[1577826000, 1606770000]], 'irt': [[1609448400, 1638306000]], 'pet': [[1609448400, 1638306000]]}

jsonpost2a host-ip/data-request/
post:
-format=iaf or iaga2002 or add
-code= single station or list
-time= total
return:
zip

jsonpost2b host-ip/data-request/
post:
-format=iaf or iaga2002 or add
-code= single station or list
-time= certain
-day1:1 -day2:1 -mon1:1 -mon2:2 -year1:2020 -year2:2020
return:
zip