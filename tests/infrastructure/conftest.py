import pytest
from aws_cdk import App


@pytest.fixture()
def sds_id():
    return "sdsid-test"


@pytest.fixture()
def app(sds_id):
    return App(context={"SDSID": sds_id})
