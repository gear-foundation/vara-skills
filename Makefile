.PHONY: test-layout verify

test-layout:
	python3 tests/test_repo_layout.py

verify: test-layout
