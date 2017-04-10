apt-get install postgresql

# cambiar metodo de autenticación en el archivo
# /etc/postgresql/9.4/main/pg_hba.conf

#local   all             postgres                                trust
#local   all             all                                     trust
#host    all             all             127.0.0.1/32            trust

# reiniciar servicio postgresql

# cambiar el password de postgres
psql -U postgres
ALTER USER postgres with password 'new-password';

#su postgres
#psql 
CREATE DATABASE dbname OWNER rolename;

#DROP 
DROP DATABASE "YourDatabase";


