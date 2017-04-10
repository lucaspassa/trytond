#run trytond

./trytond/bin/trytond -c trytond/etc/trytond.conf --verbose

#setear base de datos

./trytond/bin/trytond-admin -c trytond/etc/trytond.conf -d <nombre_base> --all -l es --verbose
