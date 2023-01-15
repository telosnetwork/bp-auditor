#!/usr/bin/env python3


def validate_bp_json(bp_json: dict):
    assert 'producer_account_name' in bp_json
    assert 'org' in bp_json
    assert 'nodes' in bp_json


def validate_block(block: dict):
    assert "timestamp" in block
    assert "producer" in block
    assert "confirmed" in block
    assert "previous" in block
    assert "transaction_mroot" in block
    assert "action_mroot" in block
    assert "schedule_version" in block
    assert "new_producers" in block
    assert "producer_signature" in block
    assert "transactions" in block
    assert "id" in block
    assert "block_num" in block
    assert "ref_block_prefix" in block
