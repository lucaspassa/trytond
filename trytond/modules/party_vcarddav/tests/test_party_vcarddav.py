# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest
import vobject
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool


class PartyVCardDAVTestCase(ModuleTestCase):
    'Test PartyVCardDAV module'
    module = 'party_vcarddav'

    @with_transaction()
    def test_party_vcard_report(self):
        'Test Party VCARD report'
        pool = Pool()
        Party = pool.get('party.party')
        VCardReport = pool.get('party_vcarddav.party.vcard', type='report')

        party1, = Party.create([{
                    'name': 'Party 1',
                    }])
        oext, content, _, _ = VCardReport.execute([party1.id], {})
        self.assertEqual(oext, 'vcf')
        self.assertIn('FN:Party 1', str(content))

    @with_transaction()
    def test_party_vcard2values(self):
        'Test Party.vcard2values'
        pool = Pool()
        Party = pool.get('party.party')

        vcard = vobject.vCard()
        vcard.add('n').value = vobject.vcard.Name('Pam Beesly')
        vcard.add('fn').value = 'Pam Beesly'
        vcard.add('email').value = 'pam@example.com'
        vcard.add('tel').value = '+55512345'

        self.assertDictEqual(
            Party().vcard2values(vcard), {
                'name': 'Pam Beesly',
                'addresses': [],
                'contact_mechanisms': [
                    ('create', [{
                                'type': 'email',
                                'value': 'pam@example.com',
                                }]),
                    ('create', [{
                                'type': 'phone',
                                'value': '+55512345',
                                }]),
                    ],
                'vcard': vcard.serialize(),
                })

        party, = Party.create([{
                    'name': 'Pam',
                    'contact_mechanisms': [
                        ('create', [{
                                    'type': 'email',
                                    'value': 'foo@example.com',
                                    }]),
                        ],
                    }])
        cm, = party.contact_mechanisms
        self.assertDictEqual(
            party.vcard2values(vcard), {
                'name': 'Pam Beesly',
                'addresses': [],
                'contact_mechanisms': [
                    ('write', [cm.id], {
                            'value': 'pam@example.com',
                            }),
                    ('create', [{
                                'type': 'phone',
                                'value': '+55512345',
                                }]),
                    ],
                'vcard': vcard.serialize(),
                })

    @with_transaction()
    def test_address_vcard2values(self):
        'Test Address.vcard2values'
        pool = Pool()
        Address = pool.get('party.address')

        values = {
            'street': '300 Cliff Street',
            'city': 'Scranton',
            'zip': '18503',
            }

        vcard = vobject.vCard()
        vcard.add('ADR')
        vcard.adr.type_param = 'HOME'
        vcard.adr.value = vobject.vcard.Address(
            street=values['street'], city=values['city'], code=values['zip'])

        self.assertDictEqual(Address.vcard2values(vcard.adr), values)


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            PartyVCardDAVTestCase))
    return suite
