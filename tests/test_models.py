
import django.db
import pytest

#from django.exception import
def test_site_create_delete(env):
    from instance.models import DjangoSite
    assert sorted(obj.uid for obj in DjangoSite.objects.all()) == []
    site0 = DjangoSite.objects.create(
        name="Example Site",
    )
    assert site0.uid == "example-site"
    assert site0.fqdn == "127.0.0.1:8000"
    assert site0.is_https is False
    assert site0.netloc == '127.0.0.1'
    assert site0.url == 'http://127.0.0.1:8000'
    assert sorted(obj.uid for obj in DjangoSite.objects.all()) == [
        "example-site",
    ]
    # uid must be unique
    with pytest.raises(django.db.IntegrityError) as e:
        site1 = DjangoSite.objects.create(
            name="Example Site",
        )
    assert e.value.message == 'column uid is not unique'
    # create with is_https=True
    site1 = DjangoSite.objects.create(
        name="Other Example",
        is_https=True,
    )
    assert site1.uid == "other-example"
    assert site1.fqdn == "127.0.0.1:8000"
    assert site1.is_https is True
    assert site1.netloc == '127.0.0.1'
    assert site1.url == 'https://127.0.0.1:8000'
    assert sorted(obj.uid for obj in DjangoSite.objects.all()) == [
        "example-site",
        "other-example",
    ]
    # create with https:// domain
    site2 = DjangoSite.objects.create(
        name="Next Example",
        fqdn="https://assets.mydomain.com/other-example/",
    )
    assert site2.uid == "next-example"
    assert site2.fqdn == "assets.mydomain.com/other-example"
    assert site2.is_https is True
    assert site2.netloc == 'assets.mydomain.com/other-example'
    assert site2.url == "https://assets.mydomain.com/other-example"
    assert sorted(obj.uid for obj in DjangoSite.objects.all()) == [
        "example-site",
        "next-example",
        "other-example",
    ]
    site0.delete()
    site1.delete()
    site2.delete()
    assert sorted(obj.uid for obj in DjangoSite.objects.all()) == []

def test_get_set_default(env):
    pass

