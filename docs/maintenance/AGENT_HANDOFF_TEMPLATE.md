# Agent Handoff

Use this template to transfer a task between agents or sessions. Remove fields that do not apply. Do not include ANSYS manuals, REA output, SDK snapshots, credentials, customer models, or other restricted data in an external handoff.

## Goal and stage

- Goal:
- Plan stage:
- Requested outcome:

## Source state

- Repository or workspace:
- Branch and commit:
- Source revision or package versions:
- Input paths and SHA-256 values, if approved to share:

## Decisions and permissions

- Decisions already made:
- Approved actions:
- Actions not approved:
- Data sharing scope:
- Intended receiver or destination:
- Receiver authorization and approval reference:
- Transferred data classes and paths:
- Transfer status: not started / sent / received / rejected:
- Receiver receipt or digest evidence:

## Work state

- Changed paths:
- Commands run and results:
- Evidence files and digests:
- User changes that must remain untouched:

## Limits

- Not checked:
- Known gaps or failures:
- Risks:

## Next action

- Next concrete action:
- Required user decision or external access:
- Stop condition:

## Safe example

This example uses a generic documentation task. It does not record a real transfer.

- Goal: Update one heading in a local project README.
- Plan stage: Documentation maintenance.
- Repository or workspace: Local sample workspace.
- Branch and commit: Use the values from the receiving workspace.
- Decisions already made: Keep the existing section order.
- Approved actions: Edit the named README file.
- Actions not approved: Run commands, contact a remote host, or share files.
- Changed paths: `README.md`.
- Commands run and results: None.
- Not checked: Rendered output and remote handoff.
- Next concrete action: Review the local diff.
- Stop condition: Stop if the request affects files outside the named workspace.


A filled destination or transfer status records intent and evidence only. It does not authorize a transfer. Do not send restricted data until the sender has explicit approval and the receiver confirms access and scope.
