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
    "awesome-sails-vft": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-frontend": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-indexer": [
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
    assert "cargo sails new" in dev_env_lower
    assert "wasm32-unknown-unknown" in dev_env
    assert "wasm32v1-none" in dev_env
    assert "install-gear.sh" in dev_env or "install-gear.ps1" in dev_env
    assert "../gear" not in dev_env

    ship = read("skills/ship-sails-app/SKILL.md")
    assert "../../references/gear-execution-model.md" in ship
    assert "../../references/gear-messaging-and-replies.md" in ship
    assert "../../references/gear-gas-reservations-and-waitlist.md" in ship
    assert "../../references/sails-program-and-service-architecture.md" in ship
    assert "../../references/sails-idl-client-pipeline.md" in ship
    assert "../../references/sails-gtest-and-local-validation.md" in ship
    assert "../../references/sails-rs-imports.md" in ship
    assert "../../references/delayed-message-pattern.md" in ship
    assert "../../references/scale-binary-decoding-guide.md" in ship
    assert "../../references/voucher-and-signless-flows.md" in ship
    assert "gear-message-execution" in ship
    assert "sails-dev-env" in ship
    assert "cargo sails new" in ship
    assert "0.10" in ship
    assert "build.rs" in ship


    new_app = read("skills/sails-new-app/SKILL.md")
    assert "Sails" in new_app
    assert ".idl" in new_app and ".opt.wasm" in new_app
    assert "build.rs" in new_app
    assert "cargo sails new" in new_app
    assert "../../references/sails-idl-client-pipeline.md" in new_app
    assert "../../references/sails-program-and-service-architecture.md" in new_app
    assert "sails-dev-env" in new_app
    assert "sails-dev-env" in new_app

    feature = read("skills/sails-feature-workflow/SKILL.md")
    feature_lower = feature.lower()
    assert "gtest" in feature_lower
    assert "gear-gstd-api-map" in feature
    assert "../../references/gear-execution-model.md" in feature
    assert "../../references/gear-messaging-and-replies.md" in feature
    assert "../../references/sails-gtest-and-local-validation.md" in feature
    assert "../../references/voucher-and-signless-flows.md" in feature

    architecture = read("skills/sails-architecture/SKILL.md")
    architecture_lower = architecture.lower()
    assert "state" in architecture_lower
    assert "reservation" in architecture_lower or "waitlist" in architecture_lower
    assert "../../references/gear-sails-production-patterns.md" in architecture
    assert "../../references/sails-program-and-service-architecture.md" in architecture
    assert "../../references/gear-messaging-and-replies.md" in architecture
    assert "../../references/gear-gas-reservations-and-waitlist.md" in architecture

    idl_client = read("skills/sails-idl-client/SKILL.md")
    idl_client_lower = idl_client.lower()
    assert "sails-js" in idl_client_lower and "parseidl" in idl_client_lower
    assert "build.rs" in idl_client
    assert "../../references/sails-idl-client-pipeline.md" in idl_client

    frontend = read("skills/sails-frontend/SKILL.md")
    frontend_lower = frontend.lower()
    assert "useprogram" in frontend_lower
    assert "usesendprogramtransaction" in frontend_lower
    assert "useprepareprogramtransaction" in frontend_lower
    assert "voucherid" in frontend_lower
    assert "@gear-js/api" in frontend
    assert "../../references/sails-frontend-and-gear-js.md" in frontend
    assert "../../references/scale-binary-decoding-guide.md" in frontend

    gtest_loop = read("skills/sails-gtest/SKILL.md")
    assert "../../references/sails-gtest-and-local-validation.md" in gtest_loop
    assert "../../references/gear-gas-reservations-and-waitlist.md" in gtest_loop
    assert "../../references/gtest-patterns.md" in gtest_loop
    assert "../../references/scale-binary-decoding-guide.md" in gtest_loop
    assert "MessageId" in gtest_loop
    assert "run_next_block" in gtest_loop

    smoke = read("skills/sails-local-smoke/SKILL.md")
    smoke_lower = smoke.lower()
    assert "program id" in smoke_lower
    assert "../../references/sails-gtest-and-local-validation.md" in smoke
    assert "../../references/sails-idl-client-pipeline.md" in smoke

    execution = read("skills/gear-message-execution/SKILL.md")
    execution_lower = execution.lower()
    assert "reply" in execution_lower
    assert "reservation" in execution_lower or "waitlist" in execution_lower
    assert "../../references/gear-sails-production-patterns.md" in execution
    assert "../../references/gear-execution-model.md" in execution
    assert "../../references/gear-messaging-and-replies.md" in execution
    assert "../../references/gear-gas-reservations-and-waitlist.md" in execution
    assert "../../references/scale-binary-decoding-guide.md" in execution

    gear_execution = read("references/gear-execution-model.md")
    gear_execution_lower = gear_execution.lower()
    assert "block" in gear_execution_lower and "rollback" in gear_execution_lower
    assert "message queue" in gear_execution_lower or "queue" in gear_execution_lower

    gear_messaging = read("references/gear-messaging-and-replies.md")
    gear_messaging_lower = gear_messaging.lower()
    assert "for_reply" in gear_messaging
    assert "reply" in gear_messaging_lower
    assert "delayed" in gear_messaging_lower or "reservation" in gear_messaging_lower

    gas_waitlist = read("references/gear-gas-reservations-and-waitlist.md")
    gas_waitlist_lower = gas_waitlist.lower()
    assert "reservation" in gas_waitlist_lower and "waitlist" in gas_waitlist_lower
    assert "rent" in gas_waitlist_lower or "expiry" in gas_waitlist_lower

    production_patterns = read("references/gear-sails-production-patterns.md")
    production_patterns_lower = production_patterns.lower()
    assert "awesome-sails" in production_patterns_lower
    assert "reservationid" in production_patterns_lower
    assert "generated client" in production_patterns_lower
    assert "voucher" in production_patterns_lower and "signless" in production_patterns_lower
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
    assert "#[export]" in sails_cheatsheet
    assert "emit_event" in sails_cheatsheet
    assert "0.10" in sails_cheatsheet
    assert "../sails" not in sails_cheatsheet
    assert "Troubleshooting" in sails_cheatsheet
    assert "parity-scale-codec" in sails_cheatsheet

    idl_pipeline = read("references/sails-idl-client-pipeline.md")
    idl_pipeline_lower = idl_pipeline.lower()
    assert "build.rs" in idl_pipeline
    assert "build_client" in idl_pipeline_lower or "clientbuilder" in idl_pipeline_lower
    assert ".idl" in idl_pipeline
    assert "build.rs" in idl_pipeline
    assert 'features = ["build"]' in idl_pipeline

    frontend_ref = read("references/sails-frontend-and-gear-js.md")
    frontend_ref_lower = frontend_ref.lower()
    assert "useprogramquery" in frontend_ref_lower
    assert "useprogramevent" in frontend_ref_lower
    assert "signandsend" in frontend_ref_lower
    assert "getprogrammetadata" in frontend_ref_lower
    assert "api.message.send" in frontend_ref
    assert "wallet" in frontend_ref_lower

    validation_ref = read("references/sails-gtest-and-local-validation.md")
    validation_ref_lower = validation_ref.lower()
    assert "gtestenv" in validation_ref_lower
    assert "blockrunmode" in validation_ref_lower
    assert "program id" in validation_ref_lower
    assert "local node" in validation_ref_lower
    assert "messageid" in validation_ref_lower
    assert "blockrunresult" in validation_ref_lower
    assert "run_to_block" in validation_ref_lower

    sails_imports = read("references/sails-rs-imports.md")
    assert "0.10" in sails_imports
    assert "build.rs" in sails_imports
    assert "#[codec(crate = sails_rs::scale_codec)]" in sails_imports
    assert "#[scale_info(crate = sails_rs::scale_info)]" in sails_imports
    assert "#[export]" in sails_imports
    assert "emit_event" in sails_imports
    assert "sails-beta" in sails_imports  # points to beta branch for ReflectHash/header protocol
    assert "../sails" not in sails_imports
    assert "../awesome-sails" not in sails_imports
    assert "../dapps" not in sails_imports

    idl_client = read("skills/sails-idl-client/SKILL.md")
    assert "Generated Client Pitfalls" in idl_client

    gtest_skill = read("skills/sails-gtest/SKILL.md")
    assert "listener" in gtest_skill or "Common Pitfalls" in gtest_skill

    gtest_patterns = read("references/gtest-patterns.md")
    gtest_patterns_lower = gtest_patterns.lower()
    assert "messageid" in gtest_patterns_lower
    assert "blockrunresult" in gtest_patterns_lower
    assert "r.log()" in gtest_patterns
    assert "run_to_block" in gtest_patterns_lower
    assert "failed.contains" in gtest_patterns
    assert "Program<'_" in gtest_patterns

    delayed_message = read("references/delayed-message-pattern.md")
    delayed_message_lower = delayed_message.lower()
    assert "send_bytes_with_gas_delayed" in delayed_message
    assert "exec::program_id()" in delayed_message
    assert ".concat()" in delayed_message
    assert "msg::source() == exec::program_id()" in delayed_message
    assert "idempot" in delayed_message_lower
    assert "../sails" not in delayed_message
    assert "../awesome-sails" not in delayed_message
    assert "../dapps" not in delayed_message
    ship_no_sibling_paths = read("skills/ship-sails-app/SKILL.md")
    assert "../sails`" not in ship_no_sibling_paths

    planner = read("skills/gear-architecture-planner/SKILL.md")
    assert "../../references/sails-program-and-service-architecture.md" in planner
    assert "../../references/gear-messaging-and-replies.md" in planner
    assert "../../references/sails-idl-client-pipeline.md" in planner
    assert "gear-gstd-api-map" in planner

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
    assert "../../references/sails-rs-imports.md" in implementer
    assert "../../references/delayed-message-pattern.md" in implementer
    assert "state ownership" in implementer_lower
    assert "generated clients" in implementer_lower or "generated client" in implementer_lower
    assert "#[export]" in implementer
    assert "emit_event" in implementer
    gtest_tdd = read("skills/gtest-tdd-loop/SKILL.md")
    assert "../../references/sails-gtest-and-local-validation.md" in gtest_tdd
    assert "../../references/gear-gas-reservations-and-waitlist.md" in gtest_tdd

    token_skill = read("skills/awesome-sails-vft/SKILL.md")
    assert "../../references/awesome-sails-token-patterns.md" in token_skill
    assert "token-scope-checklist.md" in token_skill
    assert "token-crate-chooser.md" in token_skill
    assert "token-gtest-matrix.md" in token_skill

    scale_decode = read("references/scale-binary-decoding-guide.md")
    scale_decode_lower = scale_decode.lower()
    assert "decode::<T>" in scale_decode_lower or "bare scale payload" in scale_decode_lower
    assert "state.meta.wasm" in scale_decode
    assert "programmetadata" in scale_decode_lower
    assert "gear-meta" in scale_decode_lower
    assert "sails-routed" in scale_decode_lower or "sails route" in scale_decode_lower

    endpoints = read("references/vara-network-endpoints.md")
    assert "wss://rpc.vara.network" in endpoints
    assert "SS58" in endpoints
    assert "137" in endpoints
    assert "10^12" in endpoints

    bridge_contracts = read("references/vara-eth-bridge-contracts.md")
    assert "Last Verified" in bridge_contracts
    assert "Verifier" in bridge_contracts
    assert "MessageQueue" in bridge_contracts
    assert "vft-manager" in bridge_contracts

    bridge_flows = read("references/vara-eth-bridge-flows.md")
    assert "Vara" in bridge_flows
    assert "Ethereum" in bridge_flows
    assert "ZK" in bridge_flows or "zero-knowledge" in bridge_flows
    assert "fee" in bridge_flows.lower()

    voucher_ref = read("references/voucher-and-signless-flows.md")
    voucher_ref_lower = voucher_ref.lower()
    assert "when to use" in voucher_ref_lower
    assert "builder recipe" in voucher_ref_lower
    assert "api.voucher.issue" in voucher_ref
    assert "GearVoucher" in voucher_ref
    assert "signless" in voucher_ref_lower
    assert "failure" in voucher_ref_lower
    assert "lifecycle" in voucher_ref_lower
    assert "vara-wiki" not in voucher_ref_lower
    assert "../../references/voucher-and-signless-flows.md" in frontend
    assert "../../references/voucher-and-signless-flows.md" in smoke

    wallet = read("skills/vara-wallet/SKILL.md")
    assert "voucher issue" in wallet.lower()
    assert "voucher revoke" in wallet.lower()
    assert "../../references/voucher-and-signless-flows.md" in wallet

    frontend_ref = read("references/sails-frontend-and-gear-js.md")
    assert "voucher-and-signless-flows.md" in frontend_ref
    upgrade_skill = ROOT / "skills" / "vara-skills-upgrade"
    require(upgrade_skill)
    validate(upgrade_skill)

    upgrade_md = read("skills/vara-skills-upgrade/SKILL.md")
    assert "Inline upgrade flow" in upgrade_md or "Inline Upgrade Flow" in upgrade_md
    assert "UPGRADE_AVAILABLE" in upgrade_md
    assert "JUST_UPGRADED" in upgrade_md or "just-upgraded-from" in upgrade_md

    print("starter skills ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
