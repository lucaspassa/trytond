#!/bin/bash
git clone http://github.com/tryton-ar/account_ar
cd account_ar
git checkout -b 4.2 origin/4.2
cd ..

git clone http://github.com/gcoop-libre/account_coop_ar
cd account_coop_ar
git checkout -b 4.2 origin/4.2
cd ..

git clone http://github.com/tryton-ar/account_invoice_ar
cd account_invoice_ar
git checkout -b 4.2 origin/4.2
cd ..

git clone http://github.com/tryton-ar/account_check_ar
cd account_check_ar
git checkout -b 4.2 origin/4.2
cd ..

git clone http://github.com/tryton-ar/account_voucher_ar
cd account_voucher_ar
git checkout -b 4.2 origin/4.2
cd ..

git clone http://github.com/tryton-ar/account_retencion_ar
cd account_retencion_ar
git checkout -b 4.2 origin/4.2
cd ..

git clone http://github.com/tryton-ar/bank_ar
cd bank_ar
git checkout -b 4.2 origin/4.2
cd ..

git clone http://github.com/tryton-ar/party_ar
cd party_ar
git checkout -b 4.2 origin/4.2
cd ..

git clone https://github.com/gcoop-libre/cooperative_ar
cd cooperative_ar
git checkout -b 4.2 origin/4.2
cd ..
