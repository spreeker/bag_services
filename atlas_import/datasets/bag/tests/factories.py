import string

import factory
import faker
from factory import fuzzy

from .. import models

f = faker.Factory.create(locale='nl_NL')


class EigendomsverhoudingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Eigendomsverhouding

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class FinancieringswijzeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Financieringswijze

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class GebruikFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gebruik

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class LiggingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Ligging

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class StatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Status

    code = fuzzy.FuzzyText(length=4)
    omschrijving = fuzzy.FuzzyText(length=50)


class LigplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Ligplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)


class StandplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Standplaats

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)


class VerblijfsobjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Verblijfsobject

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)


class PandFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Pand

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)


class GemeenteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gemeente
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=4, chars=string.digits)


class WoonplaatsFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Woonplaats
        django_get_or_create = ('landelijk_id',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=4, chars=string.digits)
    gemeente = factory.SubFactory(GemeenteFactory)


class OpenbareRuimteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OpenbareRuimte
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    code = fuzzy.FuzzyText(length=5, chars=string.digits)
    woonplaats = factory.SubFactory(WoonplaatsFactory)
    naam = factory.LazyAttribute(lambda o: f.street_name())


class NummeraanduidingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Nummeraanduiding

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    landelijk_id = fuzzy.FuzzyText(length=16, chars=string.digits)
    huisnummer = factory.LazyAttribute(lambda o: int(f.building_number()))
    openbare_ruimte = factory.SubFactory(OpenbareRuimteFactory)
    verblijfsobject = factory.SubFactory(VerblijfsobjectFactory)


class StadsdeelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Stadsdeel
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    gemeente = factory.SubFactory(GemeenteFactory)


class BuurtFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Buurt
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=3, chars=string.digits)
    stadsdeel = factory.SubFactory(StadsdeelFactory)


class BouwblokFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Bouwblok
        django_get_or_create = ('code',)

    id = fuzzy.FuzzyText(length=14, chars=string.digits)
    code = fuzzy.FuzzyText(length=4, chars=string.digits)
    buurt = factory.SubFactory(BuurtFactory)


class GrootstedelijkGebiedFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Grootstedelijkgebied

    naam = fuzzy.FuzzyText(length=50)


class UnescoFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Unesco

    naam = fuzzy.FuzzyText(length=50)


class BuurtcombinatieFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Buurtcombinatie
        django_get_or_create = ('code',)

    naam = fuzzy.FuzzyText(length=50)
    code = fuzzy.FuzzyText(length=2)
    vollcode = fuzzy.FuzzyText(length=3)


class GebiedsgerichtwerkenFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Gebiedsgerichtwerken
        django_get_or_create = ('code',)

    naam = fuzzy.FuzzyText(length=50)
    code = fuzzy.FuzzyText(length=4)
    stadsdeel = factory.SubFactory(StadsdeelFactory)
