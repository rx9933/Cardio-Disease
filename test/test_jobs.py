import json
import pytest
import redis
from jobs import _generate_jid, _instantiate_job, _save_job, _queue_job, add_job, get_job_by_id, get_all_job_ids, delete_jobs, update_job_status
from jobs import q,jdb

def test_generate_jid() -> None:
    """Test _generate_jid function.

    Returns:
        None

    Args:
        None
    """
    assert isinstance(_generate_jid(), str)

def test_instantiate_job() -> None:
    """Test _instantiate_job function.

    Returns:
        None

    Args:
        None
    """
    jid = 'test_id'
    status = 'test_status'
    functName = 'test_work'
    parameters = {'param1': 'value1', 'param2': 'value2'}
    job_dict = _instantiate_job(jid, status, functName, parameters)
    assert job_dict['id'] == jid
    assert job_dict['status'] == status
    assert job_dict['function_name'] == functName
    assert job_dict['input_parameters'] == parameters

def test_save_job() -> None:
    """Test _save_job function.

    Returns:
        None

    Args:
        None
    """
    jid = 'test_id'
    job_dict = {'id': jid, 'status': 'test_status', 'function_name': 'test_work', 'input_parameters': {'param1': 'value1'}}
    _save_job(jid, job_dict)
    saved_job_dict = json.loads(jdb.get(jid))
    assert saved_job_dict == job_dict

def test_queue_job_get_all_jobs() -> None:
    """Test _queue_job and get_all_job_ids functions.

    Returns:
        None

    Args:
        None
    """
    jid = 'test_id'
    _queue_job(jid)
    assert (jid in get_all_job_ids())

def test_update_job_status_get_job_by_id() -> None:
    """Test update_job_status and get_job_by_id functions.

    Returns:
        None

    Args:
        None
    """
    j = add_job('test_work', {})
    jid = j["id"]
    updated_job_dict = update_job_status(f"{jid}", 'new_status', {"out":"outval"})
    assert updated_job_dict['status'] == "new_status"

def test_add_job() -> None:
    """Test add_job function.

    Returns:
        None

    Args:
        None
    """
    functName = 'test_work'
    parameters = {'param1': 'value1'}
    job_dict = add_job(functName, parameters)
    assert 'id' in job_dict
    assert 'status' in job_dict
    assert 'function_name' in job_dict
    assert 'input_parameters' in job_dict

def test_get_job_by_id() -> None:
    """Test get_job_by_id function.

    Returns:
        None

    Args:
        None
    """
    jid = 'test_id'
    job_dict = {'id': jid, 'status': 'test_status', 'function_name': 'test_work', 'input_parameters': {'param1': 'value1'}}
    _save_job(jid, job_dict)
    retrieved_job_dict = get_job_by_id(jid)
    assert retrieved_job_dict == job_dict

def test_get_all_job_ids() -> None:
    """Test get_all_job_ids function.

    Returns:
        None

    Args:
        None
    """
    q.clear()
    jdb.flushdb()
    dic1 = add_job("test_work",{"":""},"submitted")
    dic2 = add_job("test_work",{"A":""},"submitted")
    dic3 = add_job("test_work",{"1":"4"},"submitted")

    all_job_ids = get_all_job_ids()
    assert dic1["id"] in all_job_ids
    assert dic2["id"] in all_job_ids
    assert dic3["id"] in all_job_ids
    delete_jobs()
    assert dic1["id"] not in get_all_job_ids()

def test_add_delete_jobs() -> None:
    """Test add_job and delete_jobs functions.

    Returns:
        None

    Args:
        None
    """
    l = len(get_all_job_ids())
    dic = add_job("test_work",{"":""},"submitted")

    assert len(get_all_job_ids()) == l+1
    assert dic["id"] in get_all_job_ids()
    j = get_job_by_id(dic["id"])

    assert j["id"] == dic["id"]
    assert j["status"] == dic["status"]

    delete_jobs()
    assert len(get_all_job_ids()) == l
    assert dic["id"] not in get_all_job_ids()

    
