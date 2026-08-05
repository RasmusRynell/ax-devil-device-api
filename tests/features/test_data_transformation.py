"""Tests for data transformation API contracts."""

from unittest.mock import Mock

import pytest

from src.ax_devil_device_api.features.data_transformation import (
    DataTransformationClient,
)


def test_data_transformation_uses_v1beta_and_official_topic_envelope():
    client = DataTransformationClient(Mock())
    response = Mock()
    response.content = b"{}"
    response.json.return_value = {
        "status": "success",
        "data": {"topics": [{"topicName": "axis/events"}]},
    }
    response.raise_for_status = Mock()
    client.request = Mock(return_value=response)

    assert client.get_available_topics() == [{"topicName": "axis/events"}]
    assert "/data-transformation/v1beta/" in client.AVAILABLE_TOPICS_ENDPOINT.path


def test_data_transformation_accepts_201_without_response_data():
    client = DataTransformationClient(Mock())
    response = Mock()
    response.content = b""
    response.status_code = 201
    response.raise_for_status = Mock()
    client.request = Mock(return_value=response)

    assert client.create_transform("input", "output", ".key") is None


@pytest.mark.parametrize("status_code", [200, 201, 204])
def test_data_transformation_mutations_accept_success_statuses(status_code):
    client = DataTransformationClient(Mock())
    response = Mock(
        status_code=status_code, content=b"" if status_code == 204 else b"{}"
    )
    response.json.return_value = {"status": "success"}
    client.request = Mock(return_value=response)

    client.create_transform("input", "output", ".key")
    client.remove_transform("com.axis.dt.test.1")


def test_data_transformation_remove_maps_dotted_topic_to_path_segments():
    client = DataTransformationClient(Mock())
    response = Mock(status_code=204, content=b"")
    client.request = Mock(return_value=response)

    client.remove_transform("com.axis.dt.test.1")

    endpoint = client.request.call_args.args[0]
    assert endpoint.path.endswith("/com/axis/dt/test/1")


def test_data_transformation_remove_encodes_slashes_inside_topic_component():
    client = DataTransformationClient(Mock())
    response = Mock(status_code=204, content=b"")
    client.request = Mock(return_value=response)

    client.remove_transform("com.axis/dt.test.1")

    endpoint = client.request.call_args.args[0]
    assert endpoint.path.endswith("/com/axis%2Fdt/test/1")


def test_data_transformation_rejects_malformed_json():
    client = DataTransformationClient(Mock())
    response = Mock(status_code=200, content=b"not-json")
    response.json.side_effect = ValueError("bad json")
    client.request = Mock(return_value=response)

    with pytest.raises(Exception, match="invalid JSON"):
        client.list_transforms()


@pytest.mark.parametrize("data", [None, {}, ["bad"], [{"topicName": "ok"}, "bad"]])
def test_data_transformation_topics_reject_malformed_envelopes(data):
    client = DataTransformationClient(Mock())
    response = Mock(status_code=200, content=b"{}")
    response.raise_for_status = Mock()
    response.json.return_value = {"status": "success", "data": data}
    client.request = Mock(return_value=response)

    with pytest.raises(Exception, match="topic"):
        client.get_available_topics()


@pytest.mark.parametrize("data", [None, {}, ["bad"], [{"outputTopic": "ok"}, "bad"]])
def test_data_transformation_list_rejects_malformed_envelopes(data):
    client = DataTransformationClient(Mock())
    response = Mock(status_code=200, content=b"{}")
    response.raise_for_status = Mock()
    response.json.return_value = {"status": "success", "data": data}
    client.request = Mock(return_value=response)

    with pytest.raises(Exception, match="transformation"):
        client.list_transforms()
