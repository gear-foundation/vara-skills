.PHONY: test-layout test-skills test-parser test-install test-packaging test-update verify

test-layout:
	python3 tests/test_repo_layout.py

test-skills:
	python3 tests/test_skill_validation.py
	python3 tests/test_skill_catalog.py
	python3 tests/test_gstd_api_map_skill.py

test-parser:
	python3 tests/test_parse_test_output.py

test-install:
	python3 tests/test_install_codex_skills.py

test-packaging:
	python3 tests/test_packaging_metadata.py

test-update:
	python3 tests/test_update_check.py

verify: test-layout test-skills test-parser test-install test-packaging test-update
