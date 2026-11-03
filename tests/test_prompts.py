from src.prompts import CANARY, VERSIONS

CHUNKS = [{"doc_id": "global_entry", "text": "Global Entry membership is valid for 5 years."}]


def test_all_versions_build_messages_with_canary():
    for name, version in VERSIONS.items():
        msgs = version.build("How long is Global Entry valid?",
                             CHUNKS if version.uses_retrieval else [])
        assert msgs[0]["role"] == "system"
        assert CANARY in msgs[0]["content"], name


def test_only_v1_skips_retrieval():
    assert VERSIONS["v1_baseline"].uses_retrieval is False
    assert all(v.uses_retrieval for k, v in VERSIONS.items() if k != "v1_baseline")


def test_only_v4_expects_json_and_is_hardened():
    assert VERSIONS["v4_hardened_json"].expects_json is True
    assert VERSIONS["v4_hardened_json"].hardened is True
    assert all(not v.expects_json for k, v in VERSIONS.items() if k != "v4_hardened_json")
