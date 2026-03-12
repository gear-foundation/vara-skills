#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-skill.py"
STARTER_SKILLS = {
    "gear-message-execution": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-dev-env": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "ship-sails-app": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-new-app": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-feature-workflow": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-architecture": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-idl-client": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-gtest": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-local-smoke": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
}


def require(path: Path) -> None:
    assert path.exists(), f"missing expected path: {path.relative_to(ROOT)}"


def validate(skill_dir: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(skill_dir)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def main() -> int:
    require(VALIDATOR)
    require(ROOT / "SKILL.md")

    for skill_name, expected_paths in STARTER_SKILLS.items():
        skill_dir = ROOT / "skills" / skill_name
        require(skill_dir)
        for relative in expected_paths:
            require(skill_dir / relative)
        validate(skill_dir)

    router = read("SKILL.md")
    assert "ship-sails-app" in router
    assert "sails-dev-env" in router
    assert "Codex" in router and "Claude" in router and "OpenClaw" in router

    dev_env = read("skills/sails-dev-env/SKILL.md")
    dev_env_lower = dev_env.lower()
    assert "rustup" in dev_env_lower
    assert "cargo install sails-cli" in dev_env_lower
    assert "cargo-sails" in dev_env_lower
    assert "wasm32v1-none" in dev_env
    assert "wasm32-unknown-unknown" in dev_env
    assert "macos" in dev_env_lower or "darwin" in dev_env_lower
    assert "linux" in dev_env_lower
    assert "windows" in dev_env_lower
    assert "latest" in dev_env_lower and "gear" in dev_env_lower
    assert "gear --version" in dev_env_lower
    assert "cargo sails --version" in dev_env_lower
    assert "../gear" not in dev_env

    ship = read("skills/ship-sails-app/SKILL.md")
    ship_lower = ship.lower()
    assert "ss58" in ship_lower and "0x" in ship_lower
    assert "delayed" in ship_lower and "blocks" in ship_lower and "itself" in ship_lower
    assert "voucher" in ship_lower and "signless" in ship_lower
    assert "build.rs" in ship and "cargo build" in ship_lower
    assert "../../references/gear-execution-model.md" in ship
    assert "../../references/gear-messaging-and-replies.md" in ship
    assert "../../references/gear-gas-reservations-and-waitlist.md" in ship
    assert "../../references/sails-program-and-service-architecture.md" in ship
    assert "../../references/sails-idl-client-pipeline.md" in ship
    assert "../../references/sails-gtest-and-local-validation.md" in ship
    assert "gear-message-execution" in ship
    assert "sails-dev-env" in ship
    assert "sails-program-architecture-patterns" not in ship
    assert "gear-messaging-model" not in ship

    new_app = read("skills/sails-new-app/SKILL.md")
    assert "Sails" in new_app
    assert ".idl" in new_app and ".opt.wasm" in new_app
    assert "build.rs" in new_app and "cargo build" in new_app.lower()
    assert "../../references/sails-idl-client-pipeline.md" in new_app
    assert "../../references/sails-program-and-service-architecture.md" in new_app
    assert "sails-dev-env" in new_app
    assert "sails-new-program" not in new_app
    assert "sails-idl-and-client-pipeline" not in new_app

    feature = read("skills/sails-feature-workflow/SKILL.md")
    feature_lower = feature.lower()
    assert "gtest" in feature.lower()
    assert "voucher" in feature_lower and "signless" in feature_lower
    assert "generated client" in feature_lower or "typed client" in feature_lower
    assert "gear-gstd-api-map" in feature
    assert "../../references/gear-execution-model.md" in feature
    assert "../../references/gear-messaging-and-replies.md" in feature
    assert "../../references/sails-gtest-and-local-validation.md" in feature

    architecture = read("skills/sails-architecture/SKILL.md")
    architecture_lower = architecture.lower()
    assert "waitlist" in architecture_lower and "rent" in architecture_lower
    assert "cannot be prolonged" in architecture_lower or "maximum duration" in architecture_lower
    assert "reservation" in architecture_lower and "delayed" in architecture_lower
    assert "constructor" in architecture_lower and "state ownership" in architecture_lower
    assert "generated clients" in architecture_lower or "generated client" in architecture_lower
    assert "../../references/gear-sails-production-patterns.md" in architecture
    assert "../../references/sails-program-and-service-architecture.md" in architecture
    assert "../../references/gear-messaging-and-replies.md" in architecture
    assert "../../references/gear-gas-reservations-and-waitlist.md" in architecture
    assert "sails-program-architecture-patterns" not in architecture
    assert "gear-messaging-model" not in architecture

    idl_client = read("skills/sails-idl-client/SKILL.md")
    idl_client_lower = idl_client.lower()
    assert "sails-js" in idl_client_lower and "parseidl" in idl_client_lower
    assert "gearapi" in idl_client_lower and "lib.ts" in idl_client
    assert "build.rs" in idl_client
    assert "clientbuilder" in idl_client_lower or "build_client" in idl_client_lower
    assert "../../references/sails-idl-client-pipeline.md" in idl_client
    assert "sails-idl-and-client-pipeline" not in idl_client

    gtest_loop = read("skills/sails-gtest/SKILL.md")
    assert "../../references/sails-gtest-and-local-validation.md" in gtest_loop
    assert "../../references/gear-gas-reservations-and-waitlist.md" in gtest_loop
    assert "gtest-core-workflows" not in gtest_loop

    smoke = read("skills/sails-local-smoke/SKILL.md")
    smoke_lower = smoke.lower()
    assert "ss58" in smoke_lower
    assert "do not invent" in smoke_lower and "program id" in smoke_lower
    assert "seed phrase" in smoke_lower or "private key" in smoke_lower
    assert "../../references/sails-gtest-and-local-validation.md" in smoke
    assert "../../references/sails-idl-client-pipeline.md" in smoke
    assert "gear-run-local-node" not in smoke
    assert "sails-live-node-smoke" not in smoke
    assert "gear-query-program-state" not in smoke

    execution = read("skills/gear-message-execution/SKILL.md")
    execution_lower = execution.lower()
    assert "reply" in execution_lower and "timeout" in execution_lower
    assert "reservation" in execution_lower and "waitlist" in execution_lower
    assert "exec::gas_available" in execution
    assert "route prefix" in execution_lower or "generated sails clients" in execution_lower
    assert "../../references/gear-sails-production-patterns.md" in execution
    assert "../../references/gear-execution-model.md" in execution
    assert "../../references/gear-messaging-and-replies.md" in execution
    assert "../../references/gear-gas-reservations-and-waitlist.md" in execution

    gear_execution = read("references/gear-execution-model.md")
    gear_execution_lower = gear_execution.lower()
    assert "block" in gear_execution_lower and "rollback" in gear_execution_lower
    assert "message queue" in gear_execution_lower or "queue" in gear_execution_lower

    gear_messaging = read("references/gear-messaging-and-replies.md")
    gear_messaging_lower = gear_messaging.lower()
    assert "for_reply" in gear_messaging
    assert "reply hook" in gear_messaging_lower
    assert "delayed" in gear_messaging_lower and "commit" in gear_messaging_lower
    assert "exec::gas_available" in gear_messaging
    assert "route prefix" in gear_messaging_lower
    assert "raw struct" in gear_messaging_lower

    gas_waitlist = read("references/gear-gas-reservations-and-waitlist.md")
    gas_waitlist_lower = gas_waitlist.lower()
    assert "reservation" in gas_waitlist_lower and "waitlist" in gas_waitlist_lower
    assert "rent" in gas_waitlist_lower or "expiry" in gas_waitlist_lower

    production_patterns = read("references/gear-sails-production-patterns.md")
    production_patterns_lower = production_patterns.lower()
    assert "awesome-sails" in production_patterns_lower
    assert "sails" in production_patterns_lower
    assert "dapps" in production_patterns_lower
    assert "refcell" in production_patterns_lower
    assert "storagerefcell" in production_patterns_lower
    assert "seed()" in production_patterns
    assert "blockrunmode" in production_patterns_lower
    assert "reply_deposit" in production_patterns_lower
    assert "reservationid" in production_patterns_lower
    assert "program-owned state" in production_patterns_lower
    assert "static hidden state" in production_patterns_lower or "static service state" in production_patterns_lower
    assert "generated client" in production_patterns_lower
    assert "fail-fast" in production_patterns_lower or "userspacepanic" in production_patterns_lower
    assert production_patterns.count("```rust") >= 4
    assert "outdated" in production_patterns_lower or "older" in production_patterns_lower
    assert "do not copy" in production_patterns_lower or "should not override" in production_patterns_lower
    assert "awesome-sails = {" in production_patterns
    assert "default-features = false" in production_patterns
    assert "vft-admin" in production_patterns_lower
    assert "vft-extension" in production_patterns_lower
    assert "vft-native-exchange" in production_patterns_lower
    assert "access-control" in production_patterns_lower
    assert "msg-tracker" in production_patterns_lower
    assert "awesome-sails-utils" in production_patterns_lower
    assert "checkedmath" in production_patterns_lower
    assert "lebytes" in production_patterns_lower
    assert "nonzero" in production_patterns_lower
    assert "pausableref" in production_patterns_lower
    assert "storagerefcell" in production_patterns_lower
    assert "examples/demo/app/src" not in production_patterns
    assert "examples/rmrk/" not in production_patterns
    assert "dapps/contracts/" not in production_patterns
    assert "awesome-sails/tests/" not in production_patterns

    sails_arch_ref = read("references/sails-program-and-service-architecture.md")
    sails_arch_ref_lower = sails_arch_ref.lower()
    assert "#[program]" in sails_arch_ref and "#[service]" in sails_arch_ref
    assert "await" in sails_arch_ref_lower and "revalidate" in sails_arch_ref_lower
    assert "returning `self`" in sails_arch_ref_lower or "returning self" in sails_arch_ref_lower
    assert "program-owned state" in sails_arch_ref_lower
    assert "static service state" in sails_arch_ref_lower

    sails_cheatsheet = read("references/sails-cheatsheet.md")
    sails_cheatsheet_lower = sails_cheatsheet.lower()
    assert "constructors" in sails_cheatsheet_lower and "return `self`" in sails_cheatsheet_lower
    assert "generated clients" in sails_cheatsheet_lower
    assert "route-prefixed" in sails_cheatsheet_lower or "route prefix" in sails_cheatsheet_lower

    idl_pipeline = read("references/sails-idl-client-pipeline.md")
    idl_pipeline_lower = idl_pipeline.lower()
    assert "build.rs" in idl_pipeline
    assert "build_client" in idl_pipeline_lower or "clientbuilder" in idl_pipeline_lower
    assert ".idl" in idl_pipeline

    validation_ref = read("references/sails-gtest-and-local-validation.md")
    validation_ref_lower = validation_ref.lower()
    assert "gtestenv" in validation_ref_lower
    assert "blockrunmode" in validation_ref_lower
    assert "program id" in validation_ref_lower
    assert "local node" in validation_ref_lower

    planner = read("skills/gear-architecture-planner/SKILL.md")
    assert "../../references/sails-program-and-service-architecture.md" in planner
    assert "../../references/gear-messaging-and-replies.md" in planner
    assert "../../references/sails-idl-client-pipeline.md" in planner
    assert "gear-gstd-api-map" in planner
    assert "sails-program-architecture-patterns" not in planner
    assert "gear-messaging-model" not in planner
    assert "sails-idl-and-client-pipeline" not in planner

    gstd_capability = read("skills/gear-gstd-api-map/SKILL.md")
    gstd_capability_lower = gstd_capability.lower()
    assert "../../references/gear-gstd-api-and-syscalls.md" in gstd_capability
    assert "gstd" in gstd_capability and "gcore" in gstd_capability and "gsys" in gstd_capability
    assert "design" in gstd_capability_lower and "debug" in gstd_capability_lower

    gstd_reference = read("references/gear-gstd-api-and-syscalls.md")
    assert "gr_send" in gstd_reference
    assert "gr_reply" in gstd_reference
    assert "gr_reserve_gas" in gstd_reference
    assert "gr_wait" in gstd_reference

    implementer = read("skills/sails-rust-implementer/SKILL.md")
    implementer_lower = implementer.lower()
    assert "../../references/gear-sails-production-patterns.md" in implementer
    assert "../../references/gear-messaging-and-replies.md" in implementer
    assert "../../references/gear-gas-reservations-and-waitlist.md" in implementer
    assert "state ownership" in implementer_lower
    assert "generated clients" in implementer_lower or "generated client" in implementer_lower
    assert "fail-fast" in implementer_lower or "panic" in implementer_lower
    assert "sails-idiomatic-dev" not in implementer
    assert "gear-messaging-model" not in implementer
    assert "gear-gas-and-value-accounting" not in implementer

    gtest_tdd = read("skills/gtest-tdd-loop/SKILL.md")
    assert "../../references/sails-gtest-and-local-validation.md" in gtest_tdd
    assert "../../references/gear-gas-reservations-and-waitlist.md" in gtest_tdd
    assert "gtest-core-workflows" not in gtest_tdd
    assert "gear-test-sails-program" not in gtest_tdd

    readme = read("README.md")
    assert "gpt-5.4" in readme, "README.md should name the first evaluation target"
    assert "ship-sails-app" in readme and "sails-local-smoke" in readme
    assert "sails-new-app" in readme and "sails-feature-workflow" in readme
    assert "sails-dev-env" in readme
    assert "provisional" in readme.lower(), "README.md should keep the catalog provisional"
    assert "12" in readme and "knowledge" in readme and "codegen" in readme
    assert "2026-03-11-gpt54-suite-report.md" in readme
    assert "sails-default-path" in readme and "no-low-level-bypass" in readme
    assert "artifact" in readme.lower()
    assert "self-contained" in readme.lower()
    assert "gear-message-execution" in readme
    assert "gear-gstd-api-map" in readme

    print("starter skills ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
