# Consistency Finalization Checklist

## Code and Configuration

- Remove temporary hard-coded paths, frame limits and forced input selections.
- Delete debug branches that are no longer needed.
- Any retained dump or replay capability is explicitly enabled and defaults to off.
- Preserve backward-compatible defaults for newly introduced configuration unless a default change was approved.
- Check all callers of shared preprocessing code and document intentionally unaffected model paths.

## Build

- Build from the recorded revision with the final configuration.
- Run the narrowest available compile, unit or integration checks.
- Record the final artifact name, size and SHA256.
- Do not rename the production artifact merely to distinguish an experiment.

## Deploy

- Confirm the target directory and overwrite policy before copying.
- Preserve or record the prior artifact for rollback.
- Verify the deployed artifact SHA256 against the local final artifact.
- Record configuration hashes on the target.

## Native Runtime Validation

- Remove all dump and replay environment variables.
- Run the agreed sample using only native C++ inputs.
- Confirm successful exit status and absence of replacement logs.
- Confirm no unexpected NPY or raw debug files were generated.
- Compare raw and semantic outputs with the agreed thresholds.

## Result Collection

- Keep production file names unless the user approves a naming change.
- Calculate hashes before and after result transfer.
- Do not overwrite a canonical result directory without explicit approval.
- Attach the final comparison summary to the experiment report.

## Completion Record

Document:

- earliest divergent stage
- root cause
- minimal retained change
- rejected hypotheses
- final build and deployment hashes
- validation commands and results
- remaining differences and accepted tolerances
- rollback path
