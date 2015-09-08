from rest_framework import serializers

from . import models


class Status(serializers.ModelSerializer):
    class Meta:
        model = models.Status
        fields = ('code', 'omschrijving')


class Eigendomsverhouding(serializers.ModelSerializer):
    class Meta:
        model = models.Eigendomsverhouding
        fields = ('code', 'omschrijving')


class Financieringswijze(serializers.ModelSerializer):
    class Meta:
        model = models.Financieringswijze
        fields = ('code', 'omschrijving')


class Gebruik(serializers.ModelSerializer):
    class Meta:
        model = models.Gebruik
        fields = ('code', 'omschrijving')


class Ligging(serializers.ModelSerializer):
    class Meta:
        model = models.Ligging
        fields = ('code', 'omschrijving')


class LocatieIngang(serializers.ModelSerializer):
    class Meta:
        model = models.LocatieIngang
        fields = ('code', 'omschrijving')


class Toegang(serializers.ModelSerializer):
    class Meta:
        model = models.Toegang
        fields = ('code', 'omschrijving')


class Gemeente(serializers.ModelSerializer):
    class Meta:
        model = models.Gemeente
        fields = (
            'id',
            'code',
            'date_modified',

            'naam',
            'verzorgingsgebied',
        )


class Stadsdeel(serializers.ModelSerializer):
    gemeente = Gemeente()

    class Meta:
        model = models.Stadsdeel
        fiels = (
            'id',
            'code',
            'date_modified',

            'naam',
            'gemeente',
        )


class Buurt(serializers.ModelSerializer):
    stadsdeel = Stadsdeel()

    class Meta:
        model = models.Buurt
        fields = (
            'id',
            'code',

            'naam',
            'stadsdeel',
        )


class Woonplaats(serializers.ModelSerializer):
    gemeente = Gemeente()

    class Meta:
        model = models.Woonplaats
        fields = (
            'id',
            'code',
            'date_modified',
            'document_mutatie',
            'document_nummer',

            'naam',
            'naam_ptt',
            'gemeente',
        )


class OpenbareRuimte(serializers.ModelSerializer):
    status = Status()
    type = serializers.CharField(source='get_type_display')
    woonplaats = Woonplaats()

    class Meta:
        model = models.OpenbareRuimte
        fields = (
            'id',
            'code',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',

            'type',
            'naam',
            'naam_ptt',
            'naam_nen',
            'straat_nummer',
            'woonplaats',
        )


class Nummeraanduiding(serializers.HyperlinkedModelSerializer):
    status = Status()
    openbare_ruimte = OpenbareRuimte()
    type = serializers.CharField(source='get_type_display')

    class Meta:
        model = models.Nummeraanduiding
        fields = (
            'id',
            'code',
            'url',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',
            'adres',

            'postcode',
            'huisnummer',
            'huisletter',
            'huisnummer_toevoeging',
            'type',
            'adres_nummer',
            'openbare_ruimte',
            'hoofdadres',
            'ligplaats',
            'standplaats',
            'verblijfsobject',
        )


class Ligplaats(serializers.HyperlinkedModelSerializer):
    status = Status()
    buurt = Buurt()
    hoofdadres = serializers.HyperlinkedRelatedField(
        source='hoofdadres.id',
        view_name='nummeraanduiding-detail',
        read_only=True,
    )

    class Meta:
        model = models.Ligplaats
        fields = (
            'id',
            'identificatie',
            'url',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',

            'geometrie',
            'hoofdadres',
            'adressen',
            'buurt',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expand = 'full' in self.context['request'].QUERY_PARAMS if self.context else False

        if expand:
            self.fields['adressen'] = serializers.ManyRelatedField(child_relation=Nummeraanduiding())


class Standplaats(serializers.HyperlinkedModelSerializer):
    status = Status()
    buurt = Buurt()
    hoofdadres = serializers.HyperlinkedRelatedField(
        source='hoofdadres.id',
        view_name='nummeraanduiding-detail',
        read_only=True,
    )

    class Meta:
        model = models.Standplaats
        fields = (
            'id',
            'identificatie',
            'url',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',

            'geometrie',
            'hoofdadres',
            'adressen',
            'buurt',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expand = 'full' in self.context['request'].QUERY_PARAMS

        if expand:
            self.fields['adressen'] = serializers.ManyRelatedField(child_relation=Nummeraanduiding())


class Verblijfsobject(serializers.HyperlinkedModelSerializer):
    status = Status()
    buurt = Buurt()
    eigendomsverhouding = Eigendomsverhouding()
    financieringswijze = Financieringswijze()
    gebruik = Gebruik()
    ligging = Ligging()
    locatie_ingang = LocatieIngang()
    toegang = Toegang()
    status_coordinaat = serializers.SerializerMethodField()
    type_woonobject = serializers.SerializerMethodField()
    gebruiksdoel = serializers.SerializerMethodField()
    hoofdadres = serializers.HyperlinkedRelatedField(
        source='hoofdadres.id',
        view_name='nummeraanduiding-detail',
        read_only=True,
    )

    class Meta:
        model = models.Verblijfsobject
        fields = (
            'id',
            'identificatie',
            'url',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',
            'bron',

            'geometrie',
            'gebruiksdoel',
            'oppervlakte',
            'bouwlaag_toegang',
            'status_coordinaat',
            'bouwlagen',
            'type_woonobject',
            'woningvoorraad',
            'aantal_kamers',
            'reden_afvoer',
            'eigendomsverhouding',
            'financieringswijze',
            'gebruik',
            'ligging',
            'locatie_ingang',
            'toegang',
            'hoofdadres',
            'adressen',
            'buurt',
            'panden',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        expand = 'full' in self.context['request'].QUERY_PARAMS

        if expand:
            self.fields['adressen'] = serializers.ManyRelatedField(child_relation=Nummeraanduiding())
            self.fields['panden'] = serializers.ManyRelatedField(child_relation=Pand())

    def get_gebruiksdoel(self, obj):
        return dict(
            code=obj.gebruiksdoel_code,
            omschrijving=obj.gebruiksdoel_omschrijving,
        )

    def get_status_coordinaat(self, obj):
        return dict(
            code=obj.status_coordinaat_code,
            omschrijving=obj.status_coordinaat_omschrijving,
        )

    def get_type_woonobject(self, obj):
        return dict(
            code=obj.type_woonobject_code,
            omschrijving=obj.type_woonobject_omschrijving,
        )


class Pand(serializers.HyperlinkedModelSerializer):
    status = Status()

    class Meta:
        model = models.Pand
        fields = (
            'id',
            'identificatie',
            'url',
            'date_modified',
            'document_mutatie',
            'document_nummer',
            'status',

            'geometrie',

            'bouwjaar',
            'hoogste_bouwlaag',
            'laagste_bouwlaag',
            'pandnummer',

            'verblijfsobjecten',
        )
