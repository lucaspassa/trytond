#Ejecutar como root

# instalar a mano por que se necesita la versión espesifica que tiene 
# * ar.cuit: CUIT (Código Único de Identificación Tributaria, Argentinian tax number)
# python-stdnum 1.5
# https://pypi.python.org/pypi/python-stdnum/1.5

wget https://pypi.python.org/packages/98/3c/1dc75d27c30416e76cfeb11fbfdb365204e036a9061c4837e716af7cdf6c/python-stdnum-1.5.tar.gz
tar zxf python-stdnum-1.5.tar.gz

#instalar pyhton-sql
hg clone http://hg.tryton.org/python-sql/
cd python-sql
python setup.py install

pip install pytz
pip install stdnum
pip install simpleeval
pip install cached_property
pip install zeep

apt-get install python-pypdf2