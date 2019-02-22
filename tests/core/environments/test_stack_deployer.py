from cluster_funk.core.environments.stack_deployer \
    import StackDeployer

from mock import MagicMock, patch, mock_open
import pytest
import boto3

STACK_DEPLOYER_PATH = 'cluster_funk.core.environments.stack_deployer.StackDeployer'

MOCK_STACK = """
Resources:
  DDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      AttributeDefinitions:
        -
          AttributeName: "ArtistId"
          AttributeType: "S"
        -
          AttributeName: "Concert"
          AttributeType: "S"
        -
          AttributeName: "TicketSales"
          AttributeType: "S"
      KeySchema:
        -
          AttributeName: "ArtistId"
          KeyType: "HASH"
        -
          AttributeName: "Concert"
          KeyType: "RANGE"
      ProvisionedThroughput:
        ReadCapacityUnits: 5
        WriteCapacityUnits: 5
"""


@pytest.fixture(scope='function')
def deployer():
    deployer = StackDeployer(
        "99-23-dslkjfdslksd-dks",
        "fakeprofile",
        "prefixit",
        "stg",
        "vpc",
        capabilities=['NONESENSE']
    )
    yield deployer


def test_stack_deploy_init(deployer):

    assert deployer.profile == "fakeprofile"
    assert deployer.capabilities == ["NONESENSE"]
    assert deployer.env == "stg"
    assert deployer.stack_name == "prefixit-stg-vpc"
    assert deployer.body_path == "./environments/stg/vpc.yml"


def test_create_and_update_stack(deployer, cloudformation_client):

    with patch("%s.%s" % (STACK_DEPLOYER_PATH, '_get_template_body'), MagicMock(return_value=MOCK_STACK)) as _template_mock:
        with patch("%s.%s" % (STACK_DEPLOYER_PATH, '_session'), MagicMock(return_value=boto3)) as _cf_mock:
            waitcreate, respcreate = deployer.create_stack(deployer._cloudformation_client())
            waitupdate, respupdate = deployer.update_stack(deployer._cloudformation_client())
            template_mock = _template_mock
            cf_mock = _cf_mock

    template_mock.assert_called_with()
    cf_mock.assert_called_with()
    assert respcreate['ResponseMetadata']['HTTPStatusCode'] == 200
    assert "arn:aws:cloudformation:us-east-1:123456789:stack/prefixit-stg-vpc" in respcreate['StackId']

    for wait in [waitcreate, waitupdate]:

        mock_waiter = MagicMock()
        wait(waiter=mock_waiter)
        mock_waiter.wait.assert_called_with(
            StackName=respcreate['StackId'],
            WaiterConfig={
                'Delay': 30,
                'MaxAttempts': 60
            }
        )


def test_deploy_create_update(deployer):

    mock_create = MagicMock(side_effect=BaseException('create error'))
    mock_update = MagicMock(side_effect=BaseException('update error'))

    with patch("%s.%s" % (STACK_DEPLOYER_PATH, 'create_stack'), mock_create):
        with patch("%s.%s" % (STACK_DEPLOYER_PATH, 'update_stack'), mock_update):
            with patch("%s.%s" % (STACK_DEPLOYER_PATH, '_cloudformation_client'), MagicMock()):
                wait, resp = deployer.deploy(create_stack_exception=BaseException, update_stack_exception=BaseException)
                assert resp == {'message': 'no changes to apply -> update error'}
                mock_create.assert_called_once()
                mock_update.assert_called_once()


def test_get_template(deployer):

    with patch('builtins.open', mock_open(read_data="exampledata")) as mock:
        output = deployer._get_template_body()
        assert output == "exampledata"
        mock.assert_called_with("./environments/stg/vpc.yml", "r")
