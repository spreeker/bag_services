# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atlas', '0045_lkikadastraalobject_aanduiding'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
CREATE VIEW atlas_geo_wkpb AS
SELECT
  b.id,
  b.inschrijfnummer,
  b.beperkingtype_id,
  bc.omschrijving,
  bd.documentnaam,
  bd.soort_besluit,
  o.aanduiding,
  o.geometrie
FROM
  atlas_beperking b,
  atlas_beperkingcode bc,
  atlas_wkpbbrondocument bd,
  atlas_lkikadastraalobject o
WHERE
  o.aanduiding = ANY(b.kadastrale_aanduidingen)
    AND
  b.beperkingtype_id = bc.code
    AND
  b.inschrijfnummer = bd.documentnummer''',
            reverse_sql='DROP VIEW atlas_geo_wkpb',
        )
    ]
