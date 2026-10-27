"""Ephemeral storage and /dev/shm reach the job creation request, and stay out of it when unset."""

import pytest
from pydantic import ValidationError

from prefect_northflank.credentials import Northflank
from prefect_northflank.worker import (
    FlattenedNorthflankJobConfiguration,
    FlattenedNorthflankVariables,
    NorthflankWorker,
)


def configuration(**storage) -> FlattenedNorthflankJobConfiguration:
    return FlattenedNorthflankJobConfiguration(
        credentials=Northflank(api_token="token"),
        project_id="project",
        deployment_external_image_path="prefecthq/prefect:3-latest",
        **storage,
    )


def test_unset_storage_leaves_the_platform_default():
    data = configuration().to_nested_config().to_api_dict()
    assert "storage" not in data["deployment"]


def test_ephemeral_storage_is_sent_in_mb():
    data = configuration(deployment_storage_ephemeral_storage_size=8192).to_nested_config().to_api_dict()
    assert data["deployment"]["storage"] == {"ephemeralStorage": {"storageSize": 8192}}


def test_shm_size_is_sent_on_its_own_or_with_ephemeral_storage():
    data = configuration(deployment_storage_shm_size=512).to_nested_config().to_api_dict()
    assert data["deployment"]["storage"] == {"shmSize": 512}
    data = configuration(
        deployment_storage_ephemeral_storage_size=2048, deployment_storage_shm_size=256
    ).to_nested_config().to_api_dict()
    assert data["deployment"]["storage"] == {"ephemeralStorage": {"storageSize": 2048}, "shmSize": 256}


def minimum(schema: dict) -> int | None:
    """An Optional field's bound sits in its anyOf branch, a plain one's at the top."""
    if "minimum" in schema:
        return schema["minimum"]
    return next((s["minimum"] for s in schema.get("anyOf", []) if "minimum" in s), None)


def test_the_work_pool_template_offers_both_variables():
    template = NorthflankWorker.get_default_base_job_template()
    properties = template["variables"]["properties"]
    assert minimum(properties["deployment_storage_ephemeral_storage_size"]) == 1024
    assert minimum(properties["deployment_storage_shm_size"]) == 64
    assert template["job_configuration"]["deployment_storage_ephemeral_storage_size"] == (
        "{{ deployment_storage_ephemeral_storage_size }}"
    )


def test_the_variables_refuse_less_than_the_platform_minimum():
    with pytest.raises(ValidationError):
        FlattenedNorthflankVariables(
            credentials=Northflank(api_token="token"), deployment_storage_ephemeral_storage_size=512
        )
