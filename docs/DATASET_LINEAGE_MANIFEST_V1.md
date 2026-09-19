# Dataset lineage manifest V1

## Purpose

This contract records a price-free, deterministic chain of custody for a newly governed NQ or
MNQ dataset. NQ and MNQ remain independent lineages. A dataset, hash, parent, replay result or
risk result from one instrument never proves anything about the other.

The validator does not open data files and does not establish economic identity by itself. A
structural PASS means only that the supplied metadata is internally coherent. The referenced
source and contract-identity evidence must still be checked against their recorded SHA-256 values.

## Required evidence

Each manifest records:

- one explicit instrument (`NQ` or `MNQ`) and contract identifier;
- a sanitized, hashed contract-identity evidence reference;
- source provider, exporter, version, acquisition time and raw filename/hash;
- dataset filename/hash, immediate parent hash and transformation command;
- bar interval, timestamp semantics, IANA timezone and DST policy;
- rollover, OHLCV, volume, session and holiday-calendar semantics;
- exactly one role: `DEVELOPMENT`, `VALIDATION`, `OOS_TEST` or `PAPER_REFERENCE`.

Required facts cannot be `UNKNOWN`, `UNVERIFIED` or `INACCESSIBLE`. Filenames cannot contain
local paths. Evidence references use sanitized identifiers, and transformation commands cannot
contain absolute or home paths. The canonical JSON contains metadata only: no OHLCV row and no
market price.

## Root and derived datasets

- An untransformed root uses `transformation_command = NONE`, has no parent and preserves the raw
  SHA-256 as its dataset SHA-256.
- A transformed dataset records a non-empty command and an immediate `parent_dataset_sha256`.
- A parent must be the recorded raw source or a registered dataset from the same instrument,
  lineage and raw source.
- Duplicate dataset identifiers/hashes, unresolved parents, cycles and NQ/MNQ parent links fail.

## OOS isolation

An `OOS_TEST` manifest must declare an `UNEXPOSED` source, a `SEALED` access state and a stable
OOS boundary identifier. A raw source cannot simultaneously feed OOS and non-OOS roles. An OOS
parent cannot feed development, validation or paper-reference data.

The known archive
`MNQ_OHLCV_2024_2025_03-26_SANS_09-26(1).zip` remains outside this clean-lineage contract as
`EXPOSED_DEVELOPMENT`. This document does not relabel it, make it OOS or prove its instrument.

## Non-claims

A valid manifest does not mean `PROVENANCE_CONFIRMED`, strategy `VALIDATED`, profitable, OOS-safe
in actual use or paper-ready. Those conclusions require the referenced evidence, reproducible
tests and the remaining AGIcore gates.
