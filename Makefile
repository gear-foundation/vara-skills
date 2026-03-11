.PHONY: test-layout test-skills test-parser test-install verify

test-layout:
	python3 tests/test_repo_layout.py

test-skills:
	python3 tests/test_skill_validation.py
	python3 tests/test_skill_catalog.py

test-parser:
	python3 tests/test_parse_test_output.py

test-install:
	python3 tests/test_install_codex_skills.py

verify: test-layout test-skills test-parser test-install
