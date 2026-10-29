"""Repository-only synthetic tests; no historical inputs, workers or strategy imports."""
from __future__ import annotations
import ast
import copy
import hashlib
import importlib.machinery
import importlib.util
import types
import io
import json
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import time
import traceback
import zipfile
import zlib

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools import ema_pullback_v2_portable_verifier_v2 as v

BASE = Path(__file__).resolve().parents[2]
SYNTHETIC_PATH = BASE/'tests/fixtures/ema_pullback_v2_portable_synthetic_v1.zip'
FIXTURE_SCHEMA = 'agicore:portable-synthetic-fixture:v1'
FIXTURE_SHA256 = 'a6f1a6c6c68cf7ed5be3c686e438d85cbd8753762fd9c7e2bb1a01d46c583dec'
EXPECTED_NATIVE_SHA256 = 'fd03c5fd04124072c155ef5a4fcf6af64037a78f07012129ab122c7f8ff7d983'
HISTORICAL_SOURCE_COMMIT = '95ef7c92a8e6a4b7a7a13d34f96a480a76619991'
SUCCESSOR_REGISTRATION = 'docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_CI_PORTABLE_SOURCE_REGISTRATION_V1.json'
SUCCESSOR_REGISTRATION_SHA256 = '37045900d919484f2e644a36a96f94efed597ddeb6ddd927779f1ef5525426e4'
SUCCESSOR_COMPLETE_CLOSURE_SHA256 = '155a6d8349f87a0ac6a48829324f417e915daf9b48b95207884660f284b897f3'
SUCCESSOR_VERIFIER_CLOSURE_SHA256 = 'c53540c52e8b3b98b1284dd59252ac954582e8b654376b57a4aa89201efd1487'
NATIVE_DEFLATE_HEX = '95925b6bdc301085dffb33f4bc015dac8bf7ad244bbb10bc25714b432962248d12535f525b5eda86fdef9d2425c96b9f8ced33e7e87c9a0716fb69c1e4cb0c09fd8c719ad3c2b6dfbe6f5882020b16df25b665f7d35c20f478d68d471c0ba6b3a360af9abe1b116ed10f30761997e2973b90dad0a096d62497aa908c8c3655491b9d8d86da045955ba42503281513aa1e12e04413299a350b246eb4c7a13324f3d92e3f54dd37edcb5fb73dfeeae5b7f682e6f4894a77980befb03a59b467fc479a127db8a0d1b60fe410df1e7da95df7e81e1bec7c78a0f8cba7623f46ccb37ec08fd4aeef644cd072c731749f3c0809c1e8b3df35997f4f831e1380d3459a6996dd5868deb40aaa737713a6dd8b496fbf50d03a93306ccc6c69c5d44304671517370820a638d5a4467d0a48a87c05182706842928a3b90753048f5e675a48b78b554b6b642d429a64a1b6259aba88db252cb1039d1cd4a2a8c406942388b9a73a809b8002d6a54cabe58d2651296e756b187f9891f05ec9b2fbba6dd5df84f5787f6707eb87ca6dd1c7c7bf5fe62df7cf0bbafbbf3cfedfed090d712ef70001a83db8e5608b72ffbb2fc1ecb1d962e9ee5ee5759e9d7d3e22cd33a477ced635c965a84902d5a40ab8107084a22cfb5e25839da86642aab73958d83984c7049132b9e4288202323ec2f51fe5f94ffcf639ddefd05'


def digest(raw):
    """Independent SHA256 primitive for the declared fixture oracle."""
    return hashlib.sha256(raw).hexdigest()


def oracle(value):
    """Independent decimal digit-by-digit serializer used as the test oracle."""
    def emit(x):
        if type(x) is dict:
            return '{'+','.join(json.dumps(k,ensure_ascii=False)+':'+emit(x[k]) for k in sorted(x))+'}'
        if type(x) is list:
            return '['+','.join(emit(c) for c in x)+']'
        if type(x) is int:
            n, digits = abs(x), []
            while n:
                n, digit = divmod(n,10)
                digits.append(chr(48+digit))
            return ('-' if x < 0 else '')+(''.join(reversed(digits)) or '0')
        return json.dumps(x,ensure_ascii=False,allow_nan=False)
    return (emit(value)+'\n').encode()


def synthetic_native():
    """Define invented bytes independently of archive contents or the verifier."""
    source = b'AGICORE_PORTABLE_SYNTHETIC_V1\nINVENTED_ROW_0001\n'
    identity = dict(schema=FIXTURE_SCHEMA, source_sha256=digest(source),
                    declaration='INVENTED_PROTOCOL_TEST_NO_TRADING_EXECUTION')
    bindings = dict(run_identity=identity, run_id_sha256=digest(oracle(identity)),
        dataset_lineage_manifest_sha256=digest(b'V9_INVENTED_LINEAGE_V1\n'),
        dataset_raw_sha256=digest(source),
        storage_addendum_sha256=digest(b'V9_SYNTHETIC_STRUCTURE_DECLARATION_V1\n'),
        complete_source_closure_sha256=digest(b'V9_INVENTED_SOURCE_IDENTITY_V1\n'),
        verifier_source_closure_sha256=digest(b'V9_INVENTED_VERIFIER_BINDING_V1\n'),
        synthetic_fixture_schema=FIXTURE_SCHEMA)
    doc = dict(synthetic_fixture_schema=FIXTURE_SCHEMA, dataset_id='portable-invented-v1',
        dataset_role='SYNTHETIC_TEST_ONLY', formalization_version=1,
        closed_trade_records=[], marked_equity_samples=[dict(ordinal=0, value=7)],
        metrics=dict(average_trade_usd=dict(denominator=3, numerator=1)),
        run_identity=identity, run_id_sha256=bindings['run_id_sha256'],
        dataset_lineage_manifest_sha256=bindings['dataset_lineage_manifest_sha256'])
    doc['output_sha256'] = digest(oracle(doc))
    return source, bindings, doc, oracle(doc)


def build_synthetic_fixture():
    """Construct declared protocol structures only; never invoke storage or replay code.

    Native DEFLATE is a frozen literal; ZIP members are sorted, stored, fixed-date
    POSIX regular files. Regeneration does not depend on the local compressor.
    Trust is derived from these external declarations, never read from the ZIP.
    """
    source, bindings, doc, native = synthetic_native()
    root, worker, bundle = 'portable-synthetic-v1/', 'invented/', 'bundle/'
    profile = dict(profile_id='PORTABLE_SYNTHETIC_FROZEN_BYTES_V1', algorithm='RAW_DEFLATE',
                   window_bits=-15, construction='FROZEN_LITERAL_BYTES_NO_RUNTIME_RECOMPRESSION')
    profile_sha = digest(oracle(profile))
    witness = oracle(dict(ordinal=0, synthetic=True))
    files = {root+worker+'reference-native.json':native,
             root+worker+'synthetic-source.Last.txt':source}
    streams = []
    for name, decoded, stored, codec in [
        ('logical_native_result', native, bytes.fromhex(NATIVE_DEFLATE_HEX), 'RAW_DEFLATE'),
        ('mark_source_witnesses', witness, witness, 'IDENTITY')]:
        h = digest(stored)
        object_name = 'objects/'+h[:2]+'/'+h+'.blob'
        files[root+bundle+object_name] = stored
        streams.append(dict(stream_id=name, uncompressed_size_bytes=len(decoded),
            uncompressed_sha256=digest(decoded), chunk_count=1, chunks=[dict(stream_id=name,
            ordinal=0, uncompressed_offset=0, uncompressed_size_bytes=len(decoded),
            uncompressed_sha256=digest(decoded), codec=codec, codec_profile_sha256=profile_sha,
            stored_size_bytes=len(stored), stored_sha256=h, object_identity=object_name)]))
    # Explicit counts are an external oracle, rather than verifier.array_counts.
    counts = {'/closed_trade_records':0, '/marked_equity_samples':1, 'mark_source_witnesses':1}
    manifest = dict(schema_id='agicore:ema-pullback-v2-recovery-evidence-bundle:v1',
                    bindings=bindings, codec_profile=profile, streams=streams,
                    required_record_counts=counts)
    files[root+bundle+'bundle-manifest.json'] = oracle(manifest)
    manifest_sha = digest(files[root+bundle+'bundle-manifest.json'])
    fields = ['dataset_id', 'dataset_role', 'formalization_version', 'metrics',
              'output_sha256', 'run_identity', 'run_id_sha256',
              'dataset_lineage_manifest_sha256', 'synthetic_fixture_schema']
    summary = {k:doc[k] for k in fields}
    summary.update(summary_schema_id='agicore:ema-pullback-v2-recovery-decision-summary:v1',
        storage_addendum_sha256=bindings['storage_addendum_sha256'],
        complete_source_closure_sha256=bindings['complete_source_closure_sha256'],
        verifier_source_closure_sha256=bindings['verifier_source_closure_sha256'],
        bundle_manifest_sha256=manifest_sha, logical_native_file_sha256=digest(native),
        logical_native_size_bytes=len(native))
    files[root+bundle+'decision-summary.json'] = oracle(summary)
    common = dict(bindings=bindings, bundle_manifest_sha256=manifest_sha,
        summary_sha256=digest(files[root+bundle+'decision-summary.json']),
        logical_native_file_sha256=digest(native), logical_native_size_bytes=len(native),
        native_output_sha256=doc['output_sha256'], required_record_counts=counts)
    production = dict(common, schema='agicore:synthetic-storage-production:v1',
                      status='PRODUCED_INCOMPLETE')
    files[root+bundle+'production-receipt.json'] = oracle(production)
    audit = dict(status='PASS', strategy_recomputed=False, observation_count=1,
                 native_output_sha256=doc['output_sha256'], synthetic_protocol_structure_only=True)
    independent = dict(common, schema='agicore:independent-synthetic-storage-verification:v1',
        status='PASS', audit=audit, production_receipt_sha256=digest(files[root+bundle+'production-receipt.json']))
    files[root+bundle+'independent-verification.json'] = oracle(independent)
    seal = dict(independent, schema='agicore:synthetic-storage-completion-seal:v1', status='COMPLETE',
                independent_verification_sha256=digest(files[root+bundle+'independent-verification.json']))
    files[root+bundle+'completion-seal.json'] = oracle(seal)
    report = dict(exit_code=0, failure=None, synthetic_protocol_structure_only=True,
        result=dict(reference_native_sha256=digest(native), reconstructed_native_sha256=digest(native),
        native_output_sha256=doc['output_sha256'], input_sha256=digest(source), status='PASS',
        completion='PASS', exact_bytes=True, logical_native_bytes=len(native), observations=1,
        bundle_manifest_sha256=manifest_sha))
    files[root+worker.rstrip('/')+'.receipt.json'] = oracle(report)
    inventory = [dict(path=n[len(root):], size_bytes=len(b), sha256=digest(b))
                 for n,b in sorted(files.items())]
    files[root+'FILE_INVENTORY.json'] = oracle(dict(file_count=len(inventory), files=inventory,
        schema='agicore:v2-recovery-storage-cross-closure-proof-inventory:v1',
        total_file_bytes=sum(e['size_bytes'] for e in inventory)))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2000,1,1,0,0,0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o444) << 16
            z.writestr(info, data)
    raw = buffer.getvalue()
    # Metadata expectations come from the declared bytes and fixed writer rules.
    members = [dict(name=n, size=len(b), compressed_size=len(b), crc32=zlib.crc32(b),
        compression=zipfile.ZIP_STORED, external_attr=(stat.S_IFREG | 0o444) << 16,
        sha256=digest(b)) for n,b in sorted(files.items())]
    trust = dict(archive_sha256=digest(raw), members=members, root=root, worker=worker, bundle=bundle,
        file_inventory_sha256=digest(files[root+'FILE_INVENTORY.json']), manifest_sha256=manifest_sha,
        bindings=bindings, profile=profile, profile_sha256=profile_sha, reference_sha256=digest(native),
        native_sha256=digest(native), embedded_output_sha256=doc['output_sha256'],
        historical_audit=audit, summary_projection_fields=fields,
        summary_sha256=digest(files[root+bundle+'decision-summary.json']),
        production_sha256=digest(files[root+bundle+'production-receipt.json']),
        independent_sha256=digest(files[root+bundle+'independent-verification.json']),
        seal_sha256=digest(files[root+bundle+'completion-seal.json']))
    return raw, trust


def repository_fixture():
    """Load only the versioned synthetic fixture and independently declared trust."""
    raw = SYNTHETIC_PATH.read_bytes()
    assert digest(raw) == FIXTURE_SHA256
    _, trust = build_synthetic_fixture()
    return raw, trust


class Fixture:
    """A detached byte map with explicit synthetic commitments."""
    def __init__(self, raw, trust):
        self.trust = copy.deepcopy(trust)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            self.infos = {i.filename: copy.copy(i) for i in z.infolist()}
            self.files = {i.filename:z.read(i) for i in z.infolist() if not i.is_dir()}
        self.root = trust['root']
        self.worker = self.root+trust['worker']
        self.bundle = self.root+trust['bundle']

    def read_json(self, path):
        return json.loads(self.files[path])

    def put_json(self, path, obj):
        self.files[path] = oracle(obj)

    def report(self):
        return self.read_json(self.root+self.trust['worker'].rstrip('/')+'.receipt.json')

    def put_report(self, report):
        self.put_json(self.root+self.trust['worker'].rstrip('/')+'.receipt.json',report)

    def manifest(self):
        return self.read_json(self.bundle+'bundle-manifest.json')

    def put_manifest(self, manifest, *, commit=True):
        self.put_json(self.bundle+'bundle-manifest.json',manifest)
        if commit:
            self.trust['manifest_sha256'] = v.sha(self.files[self.bundle+'bundle-manifest.json'])

    def raw_native(self, raw, *, same_reference=True):
        """Retarget only prerequisites before the native validation layer."""
        m = self.manifest()
        s = m['streams'][0]
        old = s['chunks'][0]['object_identity']
        del self.files[self.bundle+old]
        h = v.sha(raw)
        relative = f'objects/{h[:2]}/{h}.blob'
        self.files[self.bundle+relative] = raw
        s.update(uncompressed_sha256=h,uncompressed_size_bytes=len(raw),chunk_count=1)
        s['chunks'] = [dict(stream_id=s['stream_id'],ordinal=0,uncompressed_offset=0,
            uncompressed_size_bytes=len(raw),uncompressed_sha256=h,codec='IDENTITY',
            codec_profile_sha256=self.trust['profile_sha256'],stored_sha256=h,
            stored_size_bytes=len(raw),object_identity=relative)]
        self.put_manifest(m)
        self.trust['native_sha256'] = h
        report = self.report()
        report['result']['reconstructed_native_sha256'] = h
        report['result']['logical_native_bytes'] = len(raw)
        report['result']['bundle_manifest_sha256'] = self.trust['manifest_sha256']
        if same_reference:
            self.files[self.worker+'reference-native.json'] = raw
            self.trust['reference_sha256'] = h
            report['result']['reference_native_sha256'] = h
        self.put_report(report)

    def coherent_native(self, doc, *, fix_output=True):
        """Complete coherent synthetic artifact chain; no production execution."""
        output = v.sha(oracle({k:x for k,x in doc.items() if k != 'output_sha256'}))
        if fix_output:
            doc['output_sha256'] = output
        raw = oracle(doc)
        self.raw_native(raw)
        self.trust['embedded_output_sha256'] = output
        self.trust['historical_audit']['native_output_sha256'] = output
        report = self.report()
        report['result']['native_output_sha256'] = output
        self.put_report(report)
        m = self.manifest()
        m['required_record_counts'] = v.array_counts(doc)
        m['required_record_counts']['mark_source_witnesses'] = report['result']['observations']
        self.put_manifest(m)
        report['result']['bundle_manifest_sha256'] = self.trust['manifest_sha256']
        self.put_report(report)
        b = self.trust['bindings']
        summary = {k:doc[k] for k in self.trust['summary_projection_fields'] if k in doc}
        summary.update(summary_schema_id='agicore:ema-pullback-v2-recovery-decision-summary:v1',
            storage_addendum_sha256=b['storage_addendum_sha256'],
            complete_source_closure_sha256=b['complete_source_closure_sha256'],
            verifier_source_closure_sha256=b['verifier_source_closure_sha256'],
            bundle_manifest_sha256=self.trust['manifest_sha256'],
            logical_native_file_sha256=v.sha(raw),logical_native_size_bytes=len(raw))
        self.put_json(self.bundle+'decision-summary.json',summary)
        self.trust['summary_sha256'] = v.sha(self.files[self.bundle+'decision-summary.json'])
        common = dict(bindings=b,bundle_manifest_sha256=self.trust['manifest_sha256'],
            summary_sha256=self.trust['summary_sha256'],logical_native_file_sha256=v.sha(raw),
            logical_native_size_bytes=len(raw),native_output_sha256=output,required_record_counts=m['required_record_counts'])
        production = dict(common,schema='agicore:synthetic-storage-production:v1',status='PRODUCED_INCOMPLETE')
        self.put_json(self.bundle+'production-receipt.json',production)
        self.trust['production_sha256'] = v.sha(self.files[self.bundle+'production-receipt.json'])
        independent = dict(common,schema='agicore:independent-synthetic-storage-verification:v1',status='PASS',
            audit=self.trust['historical_audit'],production_receipt_sha256=self.trust['production_sha256'])
        self.put_json(self.bundle+'independent-verification.json',independent)
        self.trust['independent_sha256'] = v.sha(self.files[self.bundle+'independent-verification.json'])
        seal = dict(independent,schema='agicore:synthetic-storage-completion-seal:v1',status='COMPLETE',
            independent_verification_sha256=self.trust['independent_sha256'])
        self.put_json(self.bundle+'completion-seal.json',seal)
        self.trust['seal_sha256'] = v.sha(self.files[self.bundle+'completion-seal.json'])
        return raw

    def pack(self, *, refresh_inventory=True):
        """Store a synthetic ZIP in memory; record all changed trust explicitly."""
        inventory_path = self.root+'FILE_INVENTORY.json'
        if refresh_inventory:
            entries = [dict(path=n[len(self.root):],size_bytes=len(b),sha256=v.sha(b))
                       for n,b in sorted(self.files.items()) if n != inventory_path]
            self.put_json(inventory_path,dict(file_count=len(entries),files=entries,schema=v.INVENTORY_SCHEMA,
                total_file_bytes=sum(e['size_bytes'] for e in entries)))
        self.trust['file_inventory_sha256'] = v.sha(self.files[inventory_path])
        out = io.BytesIO()
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_STORED) as z:
            for name, old in self.infos.items():
                if old.is_dir():
                    i = copy.copy(old)
                    i.compress_type = zipfile.ZIP_STORED
                    z.writestr(i,b'')
            for name,b in self.files.items():
                i = zipfile.ZipInfo(name)
                i.create_system = 3
                i.external_attr = (stat.S_IFREG | 0o444) << 16
                i.compress_type = zipfile.ZIP_STORED
                z.writestr(i,b)
        raw = out.getvalue()
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            self.trust['members'] = [dict(name=i.filename,size=i.file_size,compressed_size=i.compress_size,
                crc32=i.CRC,compression=i.compress_type,external_attr=i.external_attr,sha256=v.sha(z.read(i)))
                for i in z.infolist()]
        self.trust['archive_sha256'] = v.sha(raw)
        return raw,self.trust


def expect_rejection(raw, trust, layer):
    """Require the exact intended layer, preserving its completed prefix."""
    try:
        v.verify_archive(raw,trust)
    except v.Rejected as error:
        if error.layer != layer:
            failure = AssertionError(f'Expected {layer}, observed {error.layer}; prefix={error.trace}')
            failure.counterexample_raw = raw
            failure.counterexample_trust = trust
            raise failure from error
        return dict(expected_layer=layer,observed_layer=error.layer,trace=error.trace)
    failure = AssertionError('Defect was accepted: '+layer)
    failure.counterexample_raw = raw
    failure.counterexample_trust = trust
    raise failure



def raw_path_zip(name):
    """Mutate only equal-length name spans in a deterministic one-member ZIP."""
    intended = name.encode('ascii')
    assert 0 < len(intended) <= 255
    buffer = io.BytesIO()
    info = zipfile.ZipInfo('x' * len(intended))
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o444) << 16
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as z:
        z.writestr(info, b'')
    raw = bytearray(buffer.getvalue())
    end = len(raw) - 22
    assert raw[end:end+4] == b'PK\x05\x06'
    assert struct.unpack_from('<HH', raw, end+8) == (1, 1)
    central = struct.unpack_from('<I', raw, end+16)[0]
    local = struct.unpack_from('<I', raw, central+42)[0]
    assert raw[local:local+4] == b'PK\x03\x04'
    assert raw[central:central+4] == b'PK\x01\x02'
    assert struct.unpack_from('<H', raw, local+26)[0] == len(intended)
    assert struct.unpack_from('<H', raw, central+28)[0] == len(intended)
    for start in (local+30, central+46):
        assert raw[start:start+len(intended)] == b'x' * len(intended)
        raw[start:start+len(intended)] = intended
    return bytes(raw)


def raw_path_names(raw):
    """Read local/central filename bytes independently of ZipInfo normalization."""
    end = len(raw) - 22
    assert raw[end:end+4] == b'PK\x05\x06'
    assert struct.unpack_from('<HH', raw, end+8) == (1, 1)
    central = struct.unpack_from('<I', raw, end+16)[0]
    assert raw[central:central+4] == b'PK\x01\x02'
    local = struct.unpack_from('<I', raw, central+42)[0]
    assert raw[local:local+4] == b'PK\x03\x04'
    ln = struct.unpack_from('<H', raw, local+26)[0]
    cn = struct.unpack_from('<H', raw, central+28)[0]
    return raw[local+30:local+30+ln], raw[central+46:central+46+cn]


def path_probe_trust(raw):
    """Authenticate a tiny synthetic container including its normalized allowlist."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members = [dict(name=i.filename, size=i.file_size, compressed_size=i.compress_size,
            crc32=i.CRC, compression=i.compress_type, external_attr=i.external_attr,
            sha256=v.sha(b'')) for i in z.infolist()]
    return dict(archive_sha256=v.sha(raw), members=members)


def focused_path_probes(original, trust):
    """Run only raw path probes; each negative must reach its named layer."""
    records = []
    raw = raw_path_zip('back/slash')
    assert raw_path_names(raw) == (b'back/slash', b'back/slash')
    assert v.zip_members(raw, path_probe_trust(raw)) == {'back/slash': b''}
    records.append(dict(id='FP01', status='PASS', name='valid POSIX container accepted'))
    raw = raw_path_zip('back\\slash')
    local, central = raw_path_names(raw)
    assert local == central == b'back\\slash'
    records.append(dict(id='FP02', status='PASS', name='both raw headers',
        local_hex=local.hex(), central_hex=central.hex(), zip_sha256=v.sha(raw)))
    result = expect_rejection(raw, path_probe_trust(raw), 'zip.path')
    records.append(dict(id='FP03', status='PASS', name='actual raw backslash rejection', **result))
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info = z.infolist()[0]
        assert info.orig_filename == 'back\\slash'
        assert info.filename == ('back/slash' if os.sep == '\\' else 'back\\slash')
        result = expect_rejection(raw, path_probe_trust(raw), 'zip.path')
        records.append(dict(id='FP04', status='PASS', name='normalization cannot hide original',
            orig_filename=info.orig_filename, filename=info.filename, **result))
    for case, name in [('FP05', '../traversal'), ('FP06', './alias'), ('FP07', 'back//slash')]:
        raw = raw_path_zip(name)
        assert raw_path_names(raw) == (name.encode(), name.encode())
        records.append(dict(id=case, status='PASS', name=name,
            **expect_rejection(raw, path_probe_trust(raw), 'zip.path')))
    receipt = v.verify_archive(original, trust)
    assert 'archive.file_inventory' in receipt['trace']
    records.append(dict(id='FP08', status='PASS', name='unmodified archive and inventory accepted',
        receipt=receipt))
    return records


def positive_extensions(original, original_trust):
    """Integrated IDENTITY and additional precommitted ZIP/decoder boundary probes."""
    probes = []
    def fixture():
        return Fixture(original,original_trust)
    f = fixture()
    f.coherent_native(f.read_json(f.worker+'reference-native.json'))
    raw,t = f.pack()
    v.verify_archive(raw,t)
    probes.append(dict(name='IDENTITY integrated roundtrip',status='PASS'))
    # All security probes reach the real entry point; structural checks precede inventory authentication.
    def zip_probe(name, entries, expected):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer,'w') as z:
            for info,data in entries:
                z.writestr(info,data)
        raw = buffer.getvalue()
        t = copy.deepcopy(original_trust)
        t['archive_sha256'] = v.sha(raw)
        probes.append(dict(name=name,status='PASS',**expect_rejection(raw,t,expected)))
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        zip_probe('duplicate',[('x',b''),('x',b'')],'zip.duplicate')
    for name in ['/absolute','../traversal','C:/drive']:
        zip_probe(name,[(name,b'')],'zip.path')
    raw = raw_path_zip('back\\slash')
    local, central = raw_path_names(raw)
    assert local == central == b'back\\slash'
    t = copy.deepcopy(original_trust)
    t['archive_sha256'] = v.sha(raw)
    probes.append(dict(name='back\\slash',status='PASS',local_name_hex=local.hex(),
        central_name_hex=central.hex(),**expect_rejection(raw,t,'zip.path')))
    i = zipfile.ZipInfo('symlink')
    i.create_system = 3
    i.external_attr = (stat.S_IFLNK | 0o777)<<16
    zip_probe('symlink',[(i,b'target')],'zip.symlink')
    zip_probe('unexpected',[('unexpected',b'')],'zip.inventory')
    zip_probe('oversized',[('large',b'x'*(v.MAX_ENTRY+1))],'zip.entry_limit')
    i = zipfile.ZipInfo('bomb')
    i.compress_type = zipfile.ZIP_DEFLATED
    zip_probe('ratio bomb',[(i,b'x'*100000)],'zip.expansion_ratio')
    f = fixture()
    raw,t = f.pack()
    bad = bytearray(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        i = next(i for i in z.infolist() if i.file_size)
        offset = i.header_offset+30+len(i.filename.encode())+len(i.extra)
    bad[offset] ^= 1
    t['archive_sha256'] = v.sha(bad)
    probes.append(dict(name='CRC corruption',status='PASS',**expect_rejection(bytes(bad),t,'zip.crc_or_structure')))
    raw,t = fixture().pack()
    next(m for m in t['members'] if m['size'])['sha256'] = '0'*64
    probes.append(dict(name='member digest',status='PASS',**expect_rejection(raw,t,'zip.member_digest')))
    f = fixture()
    inv = f.read_json(f.root+'FILE_INVENTORY.json')
    inv['files'][0]['size_bytes'] += 1
    f.put_json(f.root+'FILE_INVENTORY.json',inv)
    raw,t = f.pack(refresh_inventory=False)
    probes.append(dict(name='inventory metadata',status='PASS',**expect_rejection(raw,t,'inventory.metadata')))
    for defect,expected in [('truncation','shard.decode_bounds'),('trailing','shard.decode_bounds'),
            ('expansion','shard.decode_bounds'),('codec','shard.codec'),('offset','shard.order_offset'),
            ('ordinal','shard.order_offset'),('stream hash','stream.digest'),('decoded hash','shard.decoded')]:
        f = fixture()
        m = f.manifest()
        s,c = m['streams'][0],m['streams'][0]['chunks'][0]
        if defect in ('truncation','trailing'):
            old = f.bundle+c['object_identity']
            data = f.files.pop(old)
            changed = data[:-1] if defect == 'truncation' else data+b'!'
            h = v.sha(changed)
            c.update(stored_sha256=h,stored_size_bytes=len(changed),object_identity=f'objects/{h[:2]}/{h}.blob')
            f.files[f.bundle+c['object_identity']] = changed
        elif defect == 'expansion':
            s['uncompressed_size_bytes'] -= 1
            c['uncompressed_size_bytes'] -= 1
        elif defect == 'codec':
            c['codec'] = 'UNKNOWN'
        elif defect == 'offset':
            c['uncompressed_offset'] = 1
        elif defect == 'ordinal':
            c['ordinal'] = 1
        elif defect == 'stream hash':
            s['uncompressed_sha256'] = '0'*64
        else:
            c['uncompressed_sha256'] = '0'*64
        f.put_manifest(m)
        raw,t = f.pack()
        probes.append(dict(name=defect,status='PASS',**expect_rejection(raw,t,expected)))
    return probes


def mutate(case, original, trust):
    """Construct each exact targeted defect and its coherent prerequisites."""
    f = Fixture(original,trust)
    worker_receipt = f.report()
    zero = '0'*64
    if case == 'N01':
        doc = f.read_json(f.worker+'reference-native.json')
        doc['dataset_id'] += '-corrupt'
        f.coherent_native(doc)
        original_f = Fixture(original,trust)
        f.files[f.worker+'reference-native.json'] = original_f.files[f.worker+'reference-native.json']
        f.trust['reference_sha256'] = trust['reference_sha256']
        report = f.report()
        report['result']['reference_native_sha256'] = trust['reference_sha256']
        f.put_report(report)
    elif case in ('N02','N03','N05'):
        field = {'N02':'reference_native_sha256','N03':'reconstructed_native_sha256','N05':'native_output_sha256'}[case]
        worker_receipt['result'][field] = zero
        f.put_report(worker_receipt)
    elif case in ('N04','N06'):
        doc = f.read_json(f.worker+'reference-native.json')
        if case == 'N04':
            doc['output_sha256'] = zero
        else:
            del doc['output_sha256']
        f.coherent_native(doc,fix_output=False)
    elif 'N07' <= case <= 'N16':
        native = f.files[f.worker+'reference-native.json']
        if case == 'N07': changed = native[:-1]
        elif case == 'N08': changed = native+b'\n'
        elif case == 'N09': changed = native[:-1]+b'\r\n'
        elif case == 'N10': changed = b'{"closed_trade_records":[],'+native[1:]
        elif case == 'N11': changed = native.replace(b'"formalization_version":1',b'"formalization_version":-0',1)
        elif case == 'N12': changed = native.replace(b'"formalization_version":1',b'"formalization_version":01',1)
        elif case == 'N13': changed = native.replace(b'"formalization_version":1',b'"formalization_version":1.0',1)
        elif case == 'N14': changed = native.replace(b'"formalization_version":1',b'"formalization_version":1e0',1)
        elif case == 'N15': changed = b'{"zzz":null,'+native[1:]
        else: changed = b'{ '+native[1:]
        assert changed != native
        f.raw_native(changed)
    elif case in ('N17','N18'):
        m = f.manifest()
        m['bindings']['run_id_sha256' if case == 'N17' else 'complete_source_closure_sha256'] = zero
        f.put_manifest(m)
    elif case in ('N19','N20','N21','N23'):
        path = f.bundle+'independent-verification.json'
        doc = f.read_json(path)
        if case in ('N19','N20'):
            doc['logical_native_file_sha256'] = trust['manifest_sha256'] if case == 'N19' else zero
        elif case == 'N21': doc['native_output_sha256'] = zero
        else: doc['status'] = 'FAIL'
        f.put_json(path,doc)
    elif case == 'N22':
        m = f.manifest()
        m['required_record_counts']['mark_source_witnesses'] += 1
        f.put_manifest(m,commit=False)
        forged = v.sha(f.files[f.bundle+'bundle-manifest.json'])
        worker_receipt['result']['bundle_manifest_sha256'] = forged
        f.put_report(worker_receipt)
        path = f.bundle+'independent-verification.json'
        doc = f.read_json(path)
        doc['bundle_manifest_sha256'] = forged
        f.put_json(path,doc)
    elif case in ('N24','N25','N26'):
        path = f.bundle+'completion-seal.json'
        doc = f.read_json(path)
        if case == 'N24': doc['status'] = 'COMPLETE_VERIFIED'
        elif case == 'N25': doc['independent_verification_sha256'] = zero
        else: doc['bindings']['run_id_sha256'] = zero
        f.put_json(path,doc)
    elif case in ('N27','N28'):
        path = f.bundle+f.manifest()['streams'][0]['chunks'][0]['object_identity']
        if case == 'N27': del f.files[path]
        else:
            data = f.files[path]
            f.files[path] = bytes([data[0]^1])+data[1:]
    elif case in ('N29','N30'):
        path = f.bundle+('decision-summary.json' if case == 'N29' else 'production-receipt.json')
        doc = f.read_json(path)
        doc['verdict' if case == 'N29' else 'status'] = 'CORRUPTED'
        f.put_json(path,doc)
    else:
        raise AssertionError(case)
    return f.pack()



def regression_fixture(defect, original, trust):
    """Retarget only ZIP commitments so inventory defects reach their own layer."""
    f = Fixture(original,trust)
    path = f.root+'FILE_INVENTORY.json'
    inv = f.read_json(path)
    if defect == 'missing_field': del inv['total_file_bytes']
    elif defect == 'unexpected_field': inv['unexpected'] = None
    elif defect == 'incorrect_schema': inv['schema'] += '-wrong'
    elif defect == 'invalid_integer': inv['file_count'] = str(inv['file_count'])
    elif defect == 'boolean_count': inv['file_count'] = True
    elif defect == 'boolean_total': inv['total_file_bytes'] = True
    elif defect == 'incorrect_count': inv['file_count'] += 1
    elif defect == 'incorrect_total': inv['total_file_bytes'] += 1
    elif defect == 'duplicate_entry':
        inv['files'].append(copy.deepcopy(inv['files'][0])); inv['file_count'] += 1
    elif defect == 'invalid_path': inv['files'][0]['path'] = '../escape'
    elif defect == 'alias_path': inv['files'][0]['path'] = './alias'
    elif defect == 'incorrect_size': inv['files'][0]['size_bytes'] += 1
    elif defect == 'boolean_member_size': inv['files'][0]['size_bytes'] = True
    elif defect == 'incorrect_sha256': inv['files'][0]['sha256'] = '0'*64
    elif defect == 'missing_member': del f.files[f.root+inv['files'][0]['path']]
    elif defect == 'extra_member': f.files[f.root+'unlisted.txt'] = b'extra'
    f.put_json(path,inv)
    if defect == 'duplicate_json_key':
        f.files[path] = b'{"file_count":33,'+f.files[path][1:]
    elif defect == 'noncanonical': f.files[path] = b'{ '+f.files[path][1:]
    raw,t = f.pack(refresh_inventory=False)
    if defect == 'commitment': t['file_inventory_sha256'] = '0'*64
    return raw,t


def test_synthetic_fixture_commitments():
    """Compare every fixture byte to an external, deterministic declaration."""
    raw, trust = repository_fixture()
    rebuilt, expected = build_synthetic_fixture()
    assert raw == rebuilt and trust == expected and len(raw) == 14690
    _, bindings, doc, native = synthetic_native()
    assert digest(native) == EXPECTED_NATIVE_SHA256
    assert native == (json.dumps(doc, sort_keys=True, separators=(',', ':'), ensure_ascii=False)+'\n').encode()
    assert digest(native) != doc['output_sha256']
    assert trust['bindings'] == bindings and trust['reference_sha256'] == EXPECTED_NATIVE_SHA256
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        assert z.read(trust['root']+trust['worker']+'reference-native.json') == native
        assert all(i.create_system == 3 and i.date_time == (2000,1,1,0,0,0)
                   and i.compress_type == zipfile.ZIP_STORED for i in z.infolist())
        assert not any(n.endswith(('.py', '.pyc', '.log')) for n in z.namelist())


def historical_source_bytes(path):
    """Read one immutable Git blob without replacement refs or lazy fetches."""
    return subprocess.run(
        ['git', '--no-lazy-fetch', '--no-replace-objects', 'show', HISTORICAL_SOURCE_COMMIT+':'+path],
        cwd=BASE, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
    ).stdout


def assert_successor_closures(root):
    """Authenticate the successor registration and every current source byte."""
    raw = (root/SUCCESSOR_REGISTRATION).read_bytes()
    assert digest(raw) == SUCCESSOR_REGISTRATION_SHA256
    registration = json.loads(raw)
    assert oracle(registration) == raw
    assert registration['parent_registrations'][-1]['sha256'] == (
        '52a6c2fc2ecc7825344df6131d77282910ea5beaf3d410523da42861d9874b22'
    )
    for key, count, expected in [
        ('complete_source_closure', 35, SUCCESSOR_COMPLETE_CLOSURE_SHA256),
        ('verifier_source_closure', 9, SUCCESSOR_VERIFIER_CLOSURE_SHA256),
    ]:
        closure = registration[key]
        assert len(closure['files']) == count
        assert digest(oracle(closure)) == registration[key+'_sha256'] == expected
        for entry in closure['files']:
            data = (root/entry['path']).read_bytes()
            assert len(data) == entry['size_bytes'] and digest(data) == entry['sha256']


def test_registered_source_closures():
    """Verify the historical commit and current successor as distinct identities."""
    contract = v.load_contract()
    for key, count in [('complete_source_closure',35), ('verifier_source_closure',9)]:
        registration = contract['registered_sources'][key]
        assert len(registration['files']) == count
        assert digest(oracle(registration)) == contract['source_closures'][key]
        for entry in registration['files']:
            data = historical_source_bytes(entry['path'])
            assert len(data) == entry['size_bytes'] and digest(data) == entry['sha256']
    assert_successor_closures(BASE)


def test_registered_source_closures_reject_historical_drift(monkeypatch):
    """Changing one historical blob cannot be relabeled as a valid closure."""
    original = historical_source_bytes
    def corrupted(path):
        data = original(path)
        return data+b'X' if path == 'src/agicore/__init__.py' else data
    monkeypatch.setattr(sys.modules[__name__], 'historical_source_bytes', corrupted)
    with pytest.raises(AssertionError):
        test_registered_source_closures()


def test_registered_source_closures_reject_missing_historical_commit(monkeypatch):
    """An unavailable historical commit must not fall back to current files."""
    monkeypatch.setattr(sys.modules[__name__], 'HISTORICAL_SOURCE_COMMIT', '0'*40)
    with pytest.raises(subprocess.CalledProcessError):
        historical_source_bytes('src/agicore/__init__.py')


def test_registered_source_closures_reject_successor_drift(tmp_path):
    """Changing one current source cannot pass the successor closure check."""
    registration_path = tmp_path/SUCCESSOR_REGISTRATION
    registration_path.parent.mkdir(parents=True)
    registration_path.write_bytes((BASE/SUCCESSOR_REGISTRATION).read_bytes())
    registration = json.loads(registration_path.read_bytes())
    for closure in ('complete_source_closure', 'verifier_source_closure'):
        for entry in registration[closure]['files']:
            target = tmp_path/entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes((BASE/entry['path']).read_bytes())
    target = tmp_path/'tests/unit/trading/test_ema_pullback_v2_recovery_storage.py'
    target.write_bytes(target.read_bytes()+b'X')
    with pytest.raises(AssertionError):
        assert_successor_closures(tmp_path)


@pytest.mark.parametrize('case_id', ['R%02d'%n for n in range(1,20)])
def test_inventory_regression(case_id, tmp_path):
    """Each synthetic inventory defect must hit its original named layer."""
    raw, trust = repository_fixture()
    spec = next(c for c in v.load_contract()['p01_regressions'] if c['id'] == case_id)
    raw, trust = regression_fixture(spec['defect'], raw, trust)
    try:
        expect_rejection(raw, trust, spec['portable_expected_layer'])
    except BaseException:
        (tmp_path/'counterexample.zip').write_bytes(raw)
        (tmp_path/'trust.json').write_bytes(oracle(trust))
        raise


def test_focused_raw_zip_paths():
    """Use the actual raw local/central name spans on both operating systems."""
    raw, trust = repository_fixture()
    assert len(focused_path_probes(raw, trust)) == 8


def extension_module(path):
    """Describe controlled bytes as an extension fixture; never load its code."""
    name = '_agicore_portable_spec_fixture_v9'
    loader = importlib.machinery.ExtensionFileLoader(name, str(path))
    module = types.ModuleType(name)
    module.__spec__ = importlib.util.spec_from_file_location(name, str(path), loader=loader)
    module.__loader__, module.__file__ = loader, str(path)
    return module


def test_builtin_binary_identity():
    """A genuinely loaded built-in binds to verified interpreter bytes by convention."""
    result = v.module_binary_identity(sys, sys.executable)
    assert result == dict(origin='built-in', binary_location='NOT_SEPARATE_FILE', file_present=False,
        binary_sha256=digest(Path(sys.executable).read_bytes()),
        identity_method='BUILTIN_MODULE_PYTHON_EXECUTABLE_SHA256_CONVENTION')


def test_file_backed_binary_identity(tmp_path):
    """Hash independently known fixture bytes without invoking an extension loader."""
    path = tmp_path/('controlled'+importlib.machinery.EXTENSION_SUFFIXES[0])
    data = b'INERT_SYNTHETIC_EXTENSION_IDENTITY_V9\n'
    path.write_bytes(data)
    result = v.module_binary_identity(extension_module(path), sys.executable)
    assert result['origin'] == str(path) and result['binary_location'] == str(path.resolve())
    assert result['file_present'] and result['binary_sha256'] == digest(data)
    assert result['identity_method'] == 'EXTENSION_SPEC_FILE_BYTES_SHA256'


ORIGIN_REJECTIONS = [
    ('no_spec','runtime.spec.missing'), ('origin_none','runtime.origin'),
    ('frozen','runtime.origin'), ('builtin_file','runtime.builtin.file'),
    ('builtin_unregistered','runtime.builtin.registered'), ('builtin_loader','runtime.builtin.loader'),
    ('file_origin','runtime.file.origin'), ('loader_mismatch','runtime.spec.loader'),
    ('name_mismatch','runtime.spec.name'), ('source_loader','runtime.file.loader'),
    ('relative_origin','runtime.file.absolute'), ('missing_file','runtime.file.unavailable'),
    ('builtin_not_loaded','runtime.builtin.loaded')]


@pytest.mark.parametrize('defect,layer', ORIGIN_REJECTIONS)
def test_inconsistent_module_origin(defect, layer, tmp_path):
    """Unsupported identity primitives fail at their explicit provenance condition."""
    path = tmp_path/('controlled'+importlib.machinery.EXTENSION_SUFFIXES[0])
    alternate = tmp_path/('alternate'+importlib.machinery.EXTENSION_SUFFIXES[0])
    path.write_bytes(b'INERT_A\n')
    alternate.write_bytes(b'INERT_B\n')
    module = extension_module(path)
    if defect == 'no_spec': module = types.ModuleType('no_spec')
    elif defect == 'origin_none': module.__spec__.origin = None
    elif defect == 'frozen': module.__spec__.origin = 'frozen'
    elif defect in ('builtin_file','builtin_unregistered','builtin_not_loaded'):
        name = '_not_a_builtin_v9' if defect == 'builtin_unregistered' else 'sys'
        module = types.ModuleType(name)
        module.__spec__ = importlib.machinery.ModuleSpec(name, importlib.machinery.BuiltinImporter,
                                                       origin='built-in')
        module.__loader__ = importlib.machinery.BuiltinImporter
        if defect == 'builtin_file': module.__file__ = str(path)
    elif defect == 'builtin_loader': module.__spec__.origin = 'built-in'
    elif defect == 'file_origin': module.__file__ = str(alternate)
    elif defect == 'loader_mismatch': module.__loader__ = None
    elif defect == 'name_mismatch': module.__spec__.name = 'wrong_name'
    elif defect == 'source_loader':
        module.__loader__ = importlib.machinery.SourceFileLoader(module.__name__, str(path))
        module.__spec__.loader = module.__loader__
    elif defect == 'relative_origin': module.__spec__.origin = 'relative.pyd'
    elif defect == 'missing_file':
        module.__spec__.origin = str(tmp_path/'absent.pyd')
        module.__file__ = module.__spec__.origin
    with pytest.raises(v.Rejected) as caught:
        v.module_binary_identity(module, sys.executable)
    assert caught.value.layer == layer


def test_runtime_without_hostname():
    """Deny socket audit events while collecting actual local runtime identities."""
    active, events = [True], []
    def audit(event, args):
        if active[0] and event.startswith('socket.'):
            events.append(event)
            raise AssertionError('Socket primitive reached during runtime identity')
    sys.addaudithook(audit)
    try:
        result = v.runtime_identity()
    finally:
        active[0] = False
    assert events == []
    assert result['python_executable_sha256'] == digest(Path(sys.executable).read_bytes())
    assert result['source_sha256'] == digest(Path(v.__file__).read_bytes())
    assert result['hostname'] is None and not result['registered_profile_replaced']
    assert result['original_runtime_equivalence'] == 'NOT_ESTABLISHED'
    if result['zlib_file_present']:
        assert result['zlib_binary_sha256'] == digest(Path(result['zlib_binary_location']).read_bytes())
    else:
        assert result['zlib_module_origin'] == 'built-in'
        assert result['zlib_binary_sha256'] == result['python_executable_sha256']


def test_resource_reporting():
    """Check actual supported measurements without claiming an enforced limit."""
    result = v.resource_snapshot()
    assert not result['enforcement_claimed']
    if result['status'] == 'MEASURED':
        assert result['peak_working_set_bytes'] > 0
    else:
        assert result['status'] == 'NOT_MEASURED' and result['peak_working_set_bytes'] is None
        assert result['peak_commit_bytes'] is None and result['reason']


def test_unavailable_resource_reporting(monkeypatch):
    """An unsupported measurement is explicitly unavailable, never a fabricated zero."""
    with monkeypatch.context() as patch:
        patch.setattr(v.sys, 'platform', 'unsupported_test_platform')
        result = v.resource_snapshot()
    assert result['status'] == 'NOT_MEASURED'
    assert result['peak_working_set_bytes'] is None and result['peak_commit_bytes'] is None


def test_output_directories(tmp_path):
    """Unique children preserve existing files and cannot overwrite a file as a directory."""
    parent = tmp_path/'outputs'
    first, second = v.create_output_directory(parent), v.create_output_directory(parent)
    assert first != second and first.parent == second.parent == parent.resolve()
    marker = first/'portable-receipt.json'
    marker.write_bytes(b'EXISTING\n')
    with pytest.raises(v.Rejected) as caught:
        v.create_output_directory(marker)
    assert caught.value.layer == 'output.directory' and marker.read_bytes() == b'EXISTING\n'


def test_cli_explicit_trust_and_unique_receipts(tmp_path, capsys):
    """Exercise the actual CLI body with repository fixture bytes and independent trust."""
    raw, trust = repository_fixture()
    path = tmp_path/'trust.json'
    path.write_bytes(oracle(trust))
    args = ['--archive',str(SYNTHETIC_PATH),'--trust',str(path),'--output-root',str(tmp_path/'receipts')]
    first = v.main(args)
    second = v.main(args)
    assert first['receipt_directory'] != second['receipt_directory']
    assert first['status'] == second['status'] == 'PASS_PORTABLE_INTEGRITY_WITH_EXPLICIT_TRUST'
    assert SYNTHETIC_PATH.read_bytes() == raw
    for result in (first, second):
        assert json.loads((Path(result['receipt_directory'])/'portable-receipt.json').read_bytes()) == result
    assert capsys.readouterr().out.count('EXPLICIT_ARCHIVE_AND_TRUST') == 2


def test_cli_trust_t01_exact_limit(tmp_path, capsys):
    """T01: admit a complete MAX_ENTRY-byte trust file with JSON whitespace."""
    original, trust = repository_fixture()
    encoded = oracle(trust)
    padding = v.MAX_ENTRY-len(encoded)
    assert padding > 0
    payload = encoded+b' \t\r\n'*(padding//4)+b' '*(padding%4)
    assert len(payload) == v.MAX_ENTRY and json.loads(payload) == trust
    path = tmp_path/'T01-trust.json'
    with path.open('xb') as f:
        f.write(payload)
    result = v.main(['--archive',str(SYNTHETIC_PATH),'--trust',str(path)])
    assert result['status'] == 'PASS_PORTABLE_INTEGRITY_WITH_EXPLICIT_TRUST'
    assert result['archive_sha256'] == FIXTURE_SHA256
    assert json.loads(capsys.readouterr().out) == result
    assert path.read_bytes() == payload and SYNTHETIC_PATH.read_bytes() == original
    (tmp_path/'T01-result.json').write_bytes(oracle(dict(case_id='T01',status='PASS',
        expected_layer='PASS',observed_layer='PASS',input_file=path.name,
        input_size_bytes=len(payload),input_sha256=digest(payload),
        trailing_whitespace_bytes=padding,fixture_sha256=FIXTURE_SHA256,receipt=result)))


def test_cli_trust_t02_oversized_prefix(tmp_path, monkeypatch):
    """T02: reject the sentinel byte before parsing any oversized trust prefix."""
    original, trust = repository_fixture()
    encoded = oracle(trust)
    payload = encoded+b' '*(v.MAX_ENTRY+1-len(encoded))+b'INVALID_TRAILING_CONTENT_V17\n'
    assert len(payload) > v.MAX_ENTRY+1
    assert json.loads(payload[:v.MAX_ENTRY+1]) == trust
    path = tmp_path/'T02-trust.json'
    with path.open('xb') as f:
        f.write(payload)
    parser_calls, original_parser = [], v.parse_json
    def observe_parser(*args, **kwargs):
        parser_calls.append(args[1])
        return original_parser(*args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(v, 'parse_json', observe_parser)
        with pytest.raises(v.Rejected) as caught:
            v.main(['--archive',str(SYNTHETIC_PATH),'--trust',str(path)])
    assert caught.value.layer == 'trust.byte_limit' and parser_calls == []
    assert path.read_bytes() == payload and SYNTHETIC_PATH.read_bytes() == original
    (tmp_path/'T02-result.json').write_bytes(oracle(dict(case_id='T02',status='PASS',
        expected_layer='trust.byte_limit',observed_layer=caught.value.layer,
        input_file=path.name,input_size_bytes=len(payload),input_sha256=digest(payload),
        sentinel_prefix_bytes=v.MAX_ENTRY+1,json_parser_calls=len(parser_calls),
        fixture_sha256=FIXTURE_SHA256,trace=caught.value.trace)))


def test_cli_trust_t03_invalid_trailing_json(tmp_path):
    """T03: reject trailing non-JSON bytes, empty input and malformed JSON."""
    original, trust = repository_fixture()
    checks = []
    for name,payload,layer in [
        ('trailing',oracle(trust)+b'INVALID_TRAILING_CONTENT_V17\n','trust.json_syntax'),
        ('empty',b'','trust.byte_limit'),
        ('malformed',b'{','trust.json_syntax')]:
        assert len(payload) <= v.MAX_ENTRY
        path = tmp_path/('T03-'+name+'-trust.json')
        with path.open('xb') as f:
            f.write(payload)
        with pytest.raises(v.Rejected) as caught:
            v.main(['--archive',str(SYNTHETIC_PATH),'--trust',str(path)])
        assert caught.value.layer == layer and path.read_bytes() == payload
        checks.append(dict(subcase=name,expected_layer=layer,observed_layer=caught.value.layer,
            input_file=path.name,input_size_bytes=len(payload),input_sha256=digest(payload),
            trace=caught.value.trace))
    assert SYNTHETIC_PATH.read_bytes() == original
    (tmp_path/'T03-result.json').write_bytes(oracle(dict(case_id='T03',status='PASS',
        expected_layer='trust.json_syntax',observed_layer=checks[0]['observed_layer'],
        fixture_sha256=FIXTURE_SHA256,checks=checks)))


def test_cli_requires_explicit_mode():
    """No argument can silently select historical or synthetic evidence."""
    with pytest.raises(SystemExit) as caught:
        v.main([])
    assert caught.value.code == 2


def test_historical_mode_rejects_synthetic_input():
    """A new fixture cannot satisfy the frozen historical archive commitment."""
    with pytest.raises(v.Rejected) as caught:
        v.main(['--historical-archive',str(SYNTHETIC_PATH)])
    assert caught.value.layer == 'zip.sha256'


def test_historical_mode_has_no_missing_input_fallback(tmp_path):
    """Absent explicitly selected historical bytes remain an error."""
    with pytest.raises(FileNotFoundError):
        v.main(['--historical-archive',str(tmp_path/'not-supplied.zip')])


def test_collection_import_boundary():
    """Statically prohibit wildcard imports and scientific/worker module imports."""
    for relative in ['tools/ema_pullback_v2_portable_verifier_v2.py',
                     'tests/unit/test_ema_pullback_v2_portable_verifier_v2.py',
                     'tests/integration/test_ema_pullback_v2_portable_verifier_v2.py']:
        tree = ast.parse((BASE/relative).read_bytes())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert all(alias.name != '*' for alias in node.names)
                assert not (node.module or '').startswith('agicore')
            if isinstance(node, ast.Import):
                assert not any(alias.name.startswith('agicore') for alias in node.names)
