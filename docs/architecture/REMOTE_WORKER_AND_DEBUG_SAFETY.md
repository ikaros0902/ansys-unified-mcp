# Remote Worker and Autonomous Debug Safety

This document defines design boundaries for Stages 4 and 5. It does not implement a remote worker or run a debug loop.

## Existing capabilities

| Component | Current behavior | Boundary |
| --- | --- | --- |
| `VenvSupervisor` | Starts a domain subprocess with `subprocess.Popen`, inherited environment variables, a repository working directory, and `PYTHONPATH`. It sends local IPC requests and can restart a worker after a connection or timeout error. | This is a local process supervisor. It is not a distributed worker service. It does not define remote identity, remote authorization, or artifact transfer policy. |
| `NamedPipeClient` | Uses a Windows named pipe or a local Unix socket for domain IPC. | A local IPC endpoint is not a remote transport. |
| Workbench client | `WorkbenchController.connect` accepts a host and defaults to `security="mtls"`. | This connects to a Workbench service. It is not a general-purpose remote ANSYS worker. |
| `PermissionGate` | Checks path boundaries and command restrictions. | It does not provide remote authentication, per-job isolation, or a complete worker command allowlist. |
| `run_with_timeout` | Bounds the wait for a blocking call. A running operation can continue after the caller receives a timeout. | A timeout does not prove that the process stopped, that output was rolled back, or that a license was released. |
| `create_manifest` | Records a file path, SHA-256 digest, semantic IDs, and a UTC timestamp. | It does not sign the record or prove which host, user, solver, or license produced the file. |

## Stage 4: distributed worker design gates

Do not start a remote worker until every gate below has an owner and an approved value.

1. **Identity and permission:** identify the user, machine, ANSYS license, and permitted product. Reject a job if any item is unknown.
2. **Version pinning:** record the solver release, service pack, SDK versions, worker image or environment, and protocol version.
3. **Input boundary:** accept files only under an approved job root. Resolve paths before access. Reject traversal, symlink escapes, and blocked file types.
4. **Command boundary:** allow named operations from a fixed registry. Do not accept arbitrary shell commands or Python source from a request.
5. **Secrets:** do not copy the caller's full environment to the worker. Provide only job-scoped credentials through an approved secret store.
6. **Isolation:** use a separate job directory and least-privilege worker identity. Do not share writable job folders across users.
7. **Timeout and cancel:** distinguish request timeout, process cancellation, solver completion, and cleanup. Report when a timed-out operation may still run.
8. **Outputs and evidence:** return a manifest with input and output digests, host identity, solver and SDK versions, job ID, exit state, timestamps, and log locations. Redact secrets from logs.
9. **Cleanup:** remove temporary data only after output hashes and job status are recorded. Preserve partial output when the caller needs it for diagnosis.

The current implementation does not satisfy these gates as a distributed worker. Workbench mTLS support does not close the other gates.

## Stage 5: bounded debug loop

Use this sequence only after the user authorizes the action and the environment has an approved isolation boundary.

1. Read the task, source evidence, and permission scope.
2. Propose a small patch and name the files and commands it will affect.
3. Stop for human approval before any action outside the approved workspace or command list.
4. Apply the patch in an isolated working tree. Preserve the input files and existing user changes.
5. Show the diff and request review before running a test, solver, or remote command.
6. Record each command, exit status, relevant output, and input/output digest.
7. Stop after the approved retry limit. Escalate repeated failures, missing evidence, permission changes, or unexpected file writes.
8. Do not create, amend, rebase, or rewrite commits. The user performs all commit, push, PR, and other remote Git actions. Do not send results to another service without explicit authorization.

A test result can support software behavior. It cannot prove solver physics or product-host behavior. A manifest can support file identity. It cannot replace the original command output or solver evidence.

## Current status

Stages 4 and 5 have design boundaries only. No remote host was contacted. No ANSYS process, solver, test suite, or autonomous repair loop was started. Runtime isolation, cancellation, rollback, and evidence collection remain unverified.


## Stage 4 job/evidence record (design only)

This example defines fields for a future worker contract. It is not an implemented schema and does not prove that any field can be collected or trusted. Keep paths relative to an approved job root. Store identity references, not credentials or full environment data.

```json
{
  "schema_version": "1.0",
  "job_id": "<unique-id>",
  "protocol_version": "<version>",
  "request": {
    "operation_id": "<registered-operation>",
    "product": "<product-id>",
    "solver_version": "<release-and-service-pack>",
    "sdk_versions": {},
    "inputs": [{"path": "input/model.dat", "sha256": "<digest>", "bytes": 0}]
  },
  "worker": {"identity_ref": "<approved-reference>", "environment_digest": "<digest>"},
  "state": "queued",
  "timestamps_utc": {"created": "<RFC3339>", "started": null, "finished": null},
  "result": {"exit_code": null, "outputs": [], "logs": []},
  "cancellation": {"requested": false, "confirmed": false},
  "cleanup": {"state": "pending", "completed_at": null},
  "evidence": {"manifest_sha256": null, "signature": null}
}
```

Allowed terminal states, cancellation confirmation, signature format, host identity source, and retention rules require an approved worker and security policy. A requested cancellation is not evidence of a stopped process. A digest is not proof of trustworthy collection.
