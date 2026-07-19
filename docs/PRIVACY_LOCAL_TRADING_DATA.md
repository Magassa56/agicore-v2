# Privacy of Local Trading Data

## Purpose

AGIcore Trading may process sensitive material locally. Real trading data and personal reports must remain outside public Git history. Public documentation and fixtures must use clearly labelled, wholly fictional values.

## Data that must remain local

Never publish real or user-derived:

- NinjaTrader or other platform exports;
- trade, order, fill and position records;
- account or broker identifiers;
- balances, profit and loss, performance statistics or risk reports;
- timestamps and instrument activity tied to a person;
- generated trader profiles, analyses and personal reports;
- screenshots, logs or metadata that reveal identity or local paths;
- credentials, API keys, tokens or environment files.

Anonymising a filename is not enough. If the underlying values came from a user or real account, the file remains private.

## Approved local locations

- `data/` stores local input data and exports. Git ignores the whole directory.
- `reports/local/` stores ordinary generated reports that must remain on the workstation.
- `reports/private/` stores explicitly sensitive or personal reports.
- Files ending in `.local.md` or `.local.json` are local-only regardless of directory.

`reports/examples/` is reserved for public examples that are entirely fictional. Never copy a real export or report into that directory and then merely replace a few labels.

## Publishing prohibition

Do not stage, commit, attach to an issue, paste into a PR or otherwise publish real exports or user-generated reports. Review staged paths and content before every authorized commit. If provenance is uncertain, treat the material as private and request human review.

## Deleting from HEAD is not deleting Git history

Removing a tracked file from the current branch removes it from the next version of HEAD after commit. A simple file deletion does not remove earlier copies from Git history: existing commits, clones, forks, caches and pull-request artifacts may still contain them.

This privacy-hardening phase does not rewrite Git history. It only removes the identified report from the current branch and adds protections against accidental republication.

## Human procedure before any history rewrite

Using `git-filter-repo` or BFG is a separate, disruptive security operation. Before either tool is used:

1. The repository owner must confirm exactly which paths and revisions contain sensitive material without redistributing that material.
2. A human security owner must assess exposure, forks, clones, release artifacts and open pull requests.
3. Maintainers and collaborators must agree on a maintenance window, backup policy and coordinated recovery plan.
4. The repository owner must explicitly authorize the selected tool, scope and required force-push operation.
5. The rewrite must be rehearsed in an isolated clone and verified before any remote history is replaced.
6. Collaborators must be instructed to discard contaminated clones and obtain a clean copy after the authorized rewrite.

Do not run `git-filter-repo`, BFG or a force push as part of routine privacy cleanup.

## Published secrets

Deleting or rewriting a file does not make an exposed secret trustworthy again. Revoke and regenerate every credential, token or key that may have been published, then update the authorized local secret store. Never commit the replacement secret.
