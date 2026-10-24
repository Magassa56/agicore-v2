"""Independent bounded ZIP integrity verifier. No strategy, producer, controller or registered verifier imports.

Historical semantic-audit claims are authenticated, not independently re-proved.
Only explicit historical mode can produce a preserved-fixture PASS.
The library accepts explicit trust to support fully integrated synthetic tests.
"""
from __future__ import annotations

import hashlib
import _imp
import argparse
import importlib.machinery
import importlib.util
import io
import json
import pathlib
import re
import stat
import sys
import time
import tempfile
import zipfile
import zlib

PROTOCOL = 'AGICORE_PORTABLE_ARCHIVE_INTEGRITY_V2'
PLAN_SHA256 = '4b524c51f36de3daffcb503b93ae8e5b8b7887e6c3bb81c6e586181923509bea'
PASS = 'PASS_PORTABLE_ARCHIVE_INTEGRITY_FOR_PRESERVED_FIXTURE'
MAX_ARCHIVE = 4 * 1024 * 1024
MAX_ENTRY = 2 * 1024 * 1024
MAX_TOTAL = MAX_STREAM = 16 * 1024 * 1024
CHUNK = 1048576


class Rejected(ValueError):
    """Named fail-closed validation layer, with completed layer evidence."""
    def __init__(self, layer, trace=()):
        super().__init__(layer + ': FAIL_CLOSED')
        self.layer = layer
        self.trace = list(trace)


def sha(raw):
    """Hash the exact supplied bytes."""
    return hashlib.sha256(raw).hexdigest()


def check(condition, layer):
    """Reject without fallback, repair or execution."""
    if not condition:
        raise Rejected(layer)


def integer_text(value):
    """Spell exact decimal integers without changing the runtime digit limit."""
    rest, tail = abs(value), []
    while rest >= 1000000000:
        rest, digit = divmod(rest, 1000000000)
        tail.append(f'{digit:09d}')
    return ('-' if value < 0 else '') + str(rest) + ''.join(reversed(tail))


def canonical(value):
    """Emit sorted compact UTF-8, exact integers, and exactly one final LF."""
    def parts(v, depth=0):
        check(depth < 100, 'json.depth')
        if type(v) is dict:
            check(all(type(k) is str for k in v), 'json.keys')
            yield b'{'
            for i, k in enumerate(sorted(v)):
                if i:
                    yield b','
                yield json.dumps(k, ensure_ascii=False).encode('utf-8')
                yield b':'
                yield from parts(v[k], depth+1)
            yield b'}'
        elif type(v) is list:
            yield b'['
            for i, child in enumerate(v):
                if i:
                    yield b','
                yield from parts(child, depth+1)
            yield b']'
        elif type(v) is int:
            token = integer_text(v)
            check(len(token.lstrip('-')) <= 10000, 'json.integer_limit')
            yield token.encode()
        else:
            check(v is None or type(v) in (str, bool), 'json.integer_only')
            yield json.dumps(v, ensure_ascii=False, allow_nan=False).encode('utf-8')
    return b''.join(parts(value)) + b'\n'


def parse_json(raw, domain, *, exact=True):
    """Bounded strict JSON, including duplicates, integers and canonical spelling."""
    check(type(raw) is bytes and 0 < len(raw) <= MAX_STREAM, domain+'.byte_limit')
    if exact:
        check(b'\r' not in raw, domain+'.crlf')
        check(raw.endswith(b'\n'), domain+'.final_lf')
        check(not raw.endswith(b'\n\n'), domain+'.trailing_lf')
    def integer(token):
        check(token != '-0', domain+'.integer_spelling')
        digits = token.lstrip('-')
        check(len(digits) <= 10000, domain+'.integer_limit')
        number = 0
        for i in range(0, len(digits), 9):
            block = digits[i:i+9]
            number = number * (10 ** len(block)) + int(block)
        return -number if token.startswith('-') else number
    def noninteger(token):
        raise Rejected(domain+'.integer_only')
    def pairs(items):
        result, previous = {}, None
        for k, v in items:
            check(k not in result, domain+'.duplicate_key')
            if exact:
                check(previous is None or k > previous, domain+'.key_order')
            result[k] = v
            previous = k
        return result
    try:
        text = raw.decode('utf-8', 'strict')
        depth, quoted, escaped = 0, False, False
        for c in text:
            if quoted:
                if c == '"' and not escaped:
                    quoted = False
                escaped = c == '\\' and not escaped
            elif c == '"':
                quoted = True
            elif c in '{[':
                depth += 1
                check(depth < 100, domain+'.depth')
            elif c in '}]':
                depth -= 1
        result = json.loads(text, parse_int=integer, parse_float=noninteger,
                            parse_constant=noninteger, object_pairs_hook=pairs)
        stack, nodes = [result], 0
        while stack:
            node = stack.pop()
            nodes += 1
            check(nodes <= 200000, domain+'.node_limit')
            if type(node) is dict:
                stack.extend(node.values())
            elif type(node) is list:
                stack.extend(node)
        if exact:
            check(canonical(result) == raw, domain+'.canonical')
        return result
    except Rejected:
        raise
    except (ValueError, UnicodeError, RecursionError, TypeError) as exc:
        raise Rejected(domain+'.json_syntax') from exc


def safe_name(info):
    """Reject filesystem aliases before any member content is read."""
    name = info.orig_filename
    check('\x00' not in name, 'zip.name')
    check(name and not name.startswith('/') and '\\' not in name and ':' not in name,
          'zip.path')
    parts = name.rstrip('/').split('/')
    check(all(p not in ('', '.', '..') for p in parts), 'zip.path')
    check(name == info.filename, 'zip.name')
    mode = info.external_attr >> 16
    check(not stat.S_ISLNK(mode), 'zip.symlink')
    check(stat.S_IFMT(mode) in (0, stat.S_IFDIR, stat.S_IFREG), 'zip.file_type')
    check(not info.is_dir() or info.file_size == 0, 'zip.directory')
    check(not (info.flag_bits & 1), 'zip.encryption')
    check(info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), 'zip.codec')


def zip_members(raw, trust):
    """Authenticate container and allowlisted inventory; never extract to disk."""
    check(type(raw) is bytes and len(raw) <= MAX_ARCHIVE, 'zip.byte_limit')
    check(sha(raw) == trust['archive_sha256'], 'zip.sha256')
    try:
        with zipfile.ZipFile(io.BytesIO(raw), 'r') as z:
            infos = z.infolist()
            check(0 < len(infos) <= 128, 'zip.member_limit')
            for i in infos:
                safe_name(i)
            names = [i.filename for i in infos]
            check(len(names) == len(set(names)), 'zip.duplicate')
            aliases = [n.rstrip('/').casefold() for n in names]
            check(len(aliases) == len(set(aliases)), 'zip.alias')
            for i in infos:
                check(0 <= i.file_size <= MAX_ENTRY, 'zip.entry_limit')
                check(i.file_size <= max(1, i.compress_size) * 200, 'zip.expansion_ratio')
            check(sum(i.file_size for i in infos) <= MAX_TOTAL, 'zip.total_limit')
            expected = {m['name']: m for m in trust['members']}
            check(len(expected) == len(trust['members']) and set(names) == set(expected), 'zip.inventory')
            files = {}
            for i in infos:
                e = expected[i.filename]
                check((i.file_size, i.compress_size, i.CRC, i.compress_type, i.external_attr) ==
                      (e['size'], e['compressed_size'], e['crc32'], e['compression'], e['external_attr']),
                      'zip.metadata')
                with z.open(i, 'r') as f:
                    b = f.read(MAX_ENTRY + 1)
                    check(not f.read(1), 'zip.entry_limit')
                check(len(b) == i.file_size and zlib.crc32(b) == i.CRC, 'zip.crc')
                check(sha(b) == e['sha256'], 'zip.member_digest')
                if not i.is_dir():
                    files[i.filename] = b
            return files
    except Rejected:
        raise
    except (zipfile.BadZipFile, OSError, RuntimeError, ValueError, zlib.error) as exc:
        raise Rejected('zip.crc_or_structure') from exc


INVENTORY_SCHEMA = 'agicore:v2-recovery-storage-cross-closure-proof-inventory:v1'


def safe_inventory_path(name):
    """Accept unambiguous POSIX relative regular-file names only."""
    check(type(name) is str and bool(name) and name.isascii()
          and not name.startswith('/') and not name.endswith('/')
          and all(ord(c) >= 32 and ord(c) != 127 for c in name)
          and not any(c in name for c in ('\\', ':', '\x00')), 'inventory.path')
    check(all(p not in ('', '.', '..') and not p.endswith((' ', '.'))
              for p in name.split('/')), 'inventory.path')


def validate_file_inventory(files, trust):
    """Authenticate the canonical four-field inventory and every covered byte."""
    root = trust['root']
    path = root+'FILE_INVENTORY.json'
    check(path in files, 'inventory.missing')
    raw = files[path]
    check(sha(raw) == trust['file_inventory_sha256'], 'inventory.commitment')
    inv = parse_json(raw, 'inventory')
    check(type(inv) is dict and set(inv) == {'file_count','files','schema','total_file_bytes'}
          and type(inv['file_count']) is int and inv['file_count'] >= 0
          and type(inv['total_file_bytes']) is int and inv['total_file_bytes'] >= 0
          and type(inv['files']) is list and type(inv['schema']) is str, 'inventory.shape')
    check(inv['schema'] == INVENTORY_SCHEMA, 'inventory.schema')
    check(inv['file_count'] == len(inv['files']), 'inventory.count')
    seen, aliases, total = set(), set(), 0
    for entry in inv['files']:
        check(type(entry) is dict and set(entry) == {'path','sha256','size_bytes'},
              'inventory.entry')
        safe_inventory_path(entry['path'])
        name = root+entry['path']
        alias = name.casefold()
        check(name not in seen and alias not in aliases and name in files and name != path,
              'inventory.members')
        seen.add(name)
        aliases.add(alias)
        check(type(entry['size_bytes']) is int and entry['size_bytes'] >= 0
              and type(entry['sha256']) is str
              and re.fullmatch('[0-9a-f]{64}', entry['sha256']) is not None
              and len(files[name]) == entry['size_bytes']
              and sha(files[name]) == entry['sha256'], 'inventory.metadata')
        total += len(files[name])
    check(seen | {path} == set(files), 'inventory.members')
    check(total == inv['total_file_bytes'], 'inventory.total')
    if trust['archive_sha256'] == '559ab5ba4c0f65b2f899b3c19c6031af71556d4571500da5ad0f10392423a07d':
        check(inv['file_count'] == 33 and total == 211623, 'inventory.reference')


def decode_stream(stream, files, prefix, profile_sha):
    """Bounded RAW_DEFLATE/IDENTITY decoder with full ordered stream verification."""
    check(set(stream) == {'stream_id','uncompressed_size_bytes','uncompressed_sha256','chunk_count','chunks'},
          'stream.shape')
    size = stream['uncompressed_size_bytes']
    check(type(size) is int and 0 < size <= MAX_STREAM, 'stream.size')
    check(type(stream['chunks']) is list and type(stream['chunk_count']) is int and
          stream['chunk_count'] == len(stream['chunks']) == (size+CHUNK-1)//CHUNK, 'stream.count')
    decoded_chunks = []
    for ordinal, c in enumerate(stream['chunks']):
        check(set(c) == {'stream_id','ordinal','uncompressed_offset','uncompressed_size_bytes',
              'uncompressed_sha256','codec','codec_profile_sha256','stored_size_bytes',
              'stored_sha256','object_identity'}, 'shard.shape')
        check(type(c['ordinal']) is int and c['ordinal'] == ordinal and
              type(c['uncompressed_offset']) is int and c['uncompressed_offset'] == ordinal*CHUNK,
              'shard.order_offset')
        n = min(CHUNK, size-ordinal*CHUNK)
        check(type(c['uncompressed_size_bytes']) is int and c['uncompressed_size_bytes'] == n,
              'shard.partition')
        check(c['stream_id'] == stream['stream_id'] and c['codec_profile_sha256'] == profile_sha,
              'shard.profile')
        h = c['stored_sha256']
        check(type(h) is str and re.fullmatch('[0-9a-f]{64}',h) is not None,
              'shard.identity')
        check(c['object_identity'] == f'objects/{h[:2]}/{h}.blob', 'shard.identity')
        check(prefix+c['object_identity'] in files, 'shard.missing')
        stored = files[prefix+c['object_identity']]
        check(type(c['stored_size_bytes']) is int and 0 < c['stored_size_bytes'] <= CHUNK
              and len(stored) == c['stored_size_bytes'] and sha(stored) == h, 'shard.stored')
        if c['codec'] == 'RAW_DEFLATE':
            check(len(stored) < n, 'shard.fallback')
            decoder = zlib.decompressobj(wbits=-15)
            try:
                decoded = decoder.decompress(stored, n+1)
            except zlib.error as exc:
                raise Rejected('shard.raw_deflate') from exc
            check(len(decoded) <= n and decoder.eof and not decoder.unused_data
                  and not decoder.unconsumed_tail, 'shard.decode_bounds')
        else:
            check(c['codec'] == 'IDENTITY', 'shard.codec')
            decoded = stored
        check(len(decoded) == n and sha(decoded) == c['uncompressed_sha256'], 'shard.decoded')
        decoded_chunks.append(decoded)
    result = b''.join(decoded_chunks)
    check(len(result) == size and sha(result) == stream['uncompressed_sha256'], 'stream.digest')
    return result


def array_counts(value, path=''):
    """Derive all JSON array counts with exact JSON Pointer escaping."""
    result = {}
    if type(value) is list:
        result[path] = len(value)
        for i, child in enumerate(value):
            result.update(array_counts(child, path+'/'+str(i)))
    elif type(value) is dict:
        for k, child in value.items():
            result.update(array_counts(child,path+'/'+k.replace('~','~0').replace('/','~1')))
    return result


def verify_archive(raw, trust):
    """Integrated archive-to-seal integrity validation using explicit external trust."""
    trace = []
    def passed(layer):
        trace.append(layer)
    try:
        files = zip_members(raw, trust)
        passed('zip.authenticated_members')
        validate_file_inventory(files, trust)
        passed('archive.file_inventory')
        root, bundle = trust['root'], trust['root']+trust['bundle']
        worker = root+trust['worker']
        def get(path):
            check(path in files, 'evidence.missing')
            return files[path]
        mraw = get(bundle+'bundle-manifest.json')
        manifest = parse_json(mraw, 'manifest')
        check(sha(mraw) == trust['manifest_sha256'], 'manifest.commitment')
        check(set(manifest) == {'schema_id','bindings','codec_profile','streams','required_record_counts'}
              and manifest['schema_id'] == 'agicore:ema-pullback-v2-recovery-evidence-bundle:v1', 'manifest.shape')
        b = manifest['bindings']
        expected_b = trust['bindings']
        check(type(b) is dict and set(b) == set(expected_b), 'bindings.shape')
        check(all(b[k] == expected_b[k] for k in b if k not in
              ('complete_source_closure_sha256','verifier_source_closure_sha256')), 'bindings.run')
        check(b == expected_b, 'bindings.source')
        passed('manifest.external_commitment_and_bindings')
        check(manifest['codec_profile'] == trust['profile'] and
              sha(canonical(manifest['codec_profile'])) == trust['profile_sha256'], 'profile.historical_commitment')
        check(type(manifest['streams']) is list and [s['stream_id'] for s in manifest['streams']] ==
              ['logical_native_result','mark_source_witnesses'], 'streams.required_order')
        required = {bundle+n for n in ('bundle-manifest.json','decision-summary.json','production-receipt.json',
                    'independent-verification.json','completion-seal.json')}
        aliases = {}
        for stream in manifest['streams']:
            for c in stream['chunks']:
                required.add(bundle+c['object_identity'])
                identity = (c['codec'],c['uncompressed_sha256'],c['uncompressed_size_bytes'])
                check(c['stored_sha256'] not in aliases or aliases[c['stored_sha256']] == identity,
                      'shard.conflicting_alias')
                aliases[c['stored_sha256']] = identity
        check({n for n in files if n.startswith(bundle)} == required, 'bundle.inventory')
        native = decode_stream(manifest['streams'][0], files, bundle, trust['profile_sha256'])
        witness = decode_stream(manifest['streams'][1], files, bundle, trust['profile_sha256'])
        passed('streams.bounded_decoding_and_all_shard_hashes')
        ref = get(worker+'reference-native.json')
        report = parse_json(get(root+trust['worker'].rstrip('/')+'.receipt.json'), 'worker_receipt', exact=False)
        result = report['result']
        check(sha(ref) == trust['reference_sha256'], 'reference.external_commitment')
        check(result['reference_native_sha256'] == sha(ref), 'reference.reported_hash')
        check(sha(native) == trust['native_sha256'], 'reconstruction.external_commitment')
        check(result['reconstructed_native_sha256'] == sha(native), 'reconstruction.reported_hash')
        check(native == ref, 'reconstruction.reference_equality')
        passed('reconstruction.native_reference_exact_bytes_and_hashes')
        document = parse_json(native,'native')
        check(type(document) is dict and 'output_sha256' in document, 'native.output_required')
        output = sha(canonical({k:v for k,v in document.items() if k != 'output_sha256'}))
        check(document['output_sha256'] == output == trust['embedded_output_sha256'], 'native.embedded_output')
        check(result['native_output_sha256'] == output, 'native.reported_output')
        passed('native.canonical_and_independent_embedded_output')
        for k in ('run_identity','run_id_sha256','dataset_lineage_manifest_sha256'):
            check(document[k] == b[k], 'native.run_binding')
        source = get(worker+'synthetic-source.Last.txt')
        check(sha(source) == b['dataset_raw_sha256'] == result['input_sha256'], 'native.source_bytes')
        check(type(report['exit_code']) is int and report['exit_code'] == 0
              and type(result['logical_native_bytes']) is int
              and type(result['observations']) is int and report['failure'] is None and result['status'] == 'PASS'
              and result['completion'] == 'PASS' and result['exact_bytes'] is True
              and result['logical_native_bytes'] == len(native), 'worker_receipt.identity')
        witnesses = [parse_json(line,'witness') for line in witness.splitlines(keepends=True)]
        counts = array_counts(document)
        counts['mark_source_witnesses'] = len(witnesses)
        check(canonical(counts) == canonical(manifest['required_record_counts']), 'manifest.record_counts')
        check(len(witnesses) == len(document['marked_equity_samples']) == result['observations'], 'witness.count')
        passed('native.source_binding_and_all_array_counts')
        sraw = get(bundle+'decision-summary.json')
        check(sha(sraw) == trust['summary_sha256'], 'summary.digest')
        summary = parse_json(sraw,'summary')
        expected_summary = {k:document[k] for k in trust['summary_projection_fields']}
        expected_summary.update(summary_schema_id='agicore:ema-pullback-v2-recovery-decision-summary:v1',
            storage_addendum_sha256=b['storage_addendum_sha256'],
            complete_source_closure_sha256=b['complete_source_closure_sha256'],
            verifier_source_closure_sha256=b['verifier_source_closure_sha256'],
            bundle_manifest_sha256=sha(mraw),logical_native_file_sha256=sha(native),logical_native_size_bytes=len(native))
        check(canonical(summary) == canonical(expected_summary), 'summary.complete_projection')
        praw = get(bundle+'production-receipt.json')
        check(sha(praw) == trust['production_sha256'], 'production.digest')
        production = parse_json(praw,'production')
        common = dict(bindings=b,bundle_manifest_sha256=sha(mraw),summary_sha256=sha(sraw),
            logical_native_file_sha256=sha(native),native_output_sha256=output,
            logical_native_size_bytes=len(native),required_record_counts=counts)
        expected_production = dict(common,schema='agicore:synthetic-storage-production:v1',status='PRODUCED_INCOMPLETE')
        check(canonical(production) == canonical(expected_production), 'production.complete_contents')
        passed('summary_and_production.full_contents_and_external_hashes')
        iraw = get(bundle+'independent-verification.json')
        independent = parse_json(iraw,'independent')
        check(independent['status'] == 'PASS', 'independent.status')
        check(independent['logical_native_file_sha256'] == sha(native), 'independent.native')
        check(independent['native_output_sha256'] == output, 'independent.output')
        check(independent['bundle_manifest_sha256'] == sha(mraw) == result['bundle_manifest_sha256'], 'independent.manifest')
        audit = trust['historical_audit']
        check(audit['status'] == 'PASS' and audit['strategy_recomputed'] is False
              and audit['observation_count'] == len(witnesses) and audit['native_output_sha256'] == output,
              'independent.historical_audit_structure')
        expected_independent = dict(common,schema='agicore:independent-synthetic-storage-verification:v1',
            status='PASS',audit=audit,production_receipt_sha256=sha(praw))
        check(canonical(independent) == canonical(expected_independent), 'independent.complete_contents')
        check(sha(iraw) == trust['independent_sha256'], 'independent.external_digest')
        passed('independent.authenticated_identity_status_and_full_contents')
        sealraw = get(bundle+'completion-seal.json')
        seal = parse_json(sealraw,'seal')
        check(seal['status'] == 'COMPLETE', 'seal.status')
        check(seal['independent_verification_sha256'] == sha(iraw), 'seal.independent_digest')
        check(canonical(seal['bindings']) == canonical(expected_b), 'seal.bindings')
        expected_seal = dict(expected_independent,schema='agicore:synthetic-storage-completion-seal:v1',
            status='COMPLETE',independent_verification_sha256=sha(iraw))
        check(canonical(seal) == canonical(expected_seal), 'seal.complete_contents')
        check(sha(sealraw) == trust['seal_sha256'], 'seal.external_digest')
        passed('seal.complete_contents_and_external_digest')
        return dict(status='PASS_PORTABLE_INTEGRITY_CHECKS', protocol=PROTOCOL, trace=trace,
            archive_sha256=sha(raw), manifest_sha256=sha(mraw), full_native_sha256=sha(native),
            embedded_output_sha256=output, native_size_bytes=len(native), witness_size_bytes=len(witness),
            shard_count=sum(s['chunk_count'] for s in manifest['streams']),
            exact_reference_equality=True,complete_seal_validation='PASS',seal_sha256=sha(sealraw),
            seal_fields=list(sorted(seal)), original_runtime_equivalence='NOT_ESTABLISHED',
            trading_semantic_equivalence='NOT_ESTABLISHED',historical_audit_semantics_recomputed=False)
    except Rejected as exc:
        exc.trace = trace + exc.trace
        raise
    except (KeyError, IndexError, ValueError, TypeError, UnicodeError, RecursionError, OverflowError) as exc:
        raise Rejected('structure.invalid_or_missing',trace) from exc


def load_contract():
    """Load the immutable plan, independently pinned in verifier source."""
    raw = (pathlib.Path(__file__).resolve().parents[1] /
           'docs/evidence/EMA_PULLBACK_V2_PORTABLE_VERIFIER_P01_CORRECTION_PLAN_V2.json').read_bytes()
    check(sha(raw) == PLAN_SHA256, 'contract.sha256')
    return parse_json(raw,'contract',exact=False)


def module_binary_identity(module, executable):
    """Validate actual import provenance; reject unexplained or inconsistent origins."""
    spec = getattr(module, '__spec__', None)
    check(isinstance(spec, importlib.machinery.ModuleSpec), 'runtime.spec.missing')
    name = getattr(module, '__name__', None)
    check(bool(name) and spec.name == name, 'runtime.spec.name')
    check(getattr(module, '__loader__', None) is spec.loader, 'runtime.spec.loader')
    exe = pathlib.Path(executable).resolve(strict=True)
    check(exe.is_file(), 'runtime.python.file')
    module_file = getattr(module, '__file__', None)
    if spec.origin == 'built-in':
        check(spec.loader is importlib.machinery.BuiltinImporter, 'runtime.builtin.loader')
        check(not spec.has_location and module_file is None, 'runtime.builtin.file')
        check(name in sys.builtin_module_names and bool(_imp.is_builtin(name)),
              'runtime.builtin.registered')
        check(sys.modules.get(name) is module and importlib.util.find_spec(name) is spec,
              'runtime.builtin.loaded')
        return dict(origin='built-in', binary_location='NOT_SEPARATE_FILE', file_present=False,
                    binary_sha256=sha(exe.read_bytes()),
                    identity_method='BUILTIN_MODULE_PYTHON_EXECUTABLE_SHA256_CONVENTION')
    check(isinstance(spec.origin, str) and spec.origin not in ('', 'frozen'), 'runtime.origin')
    check(spec.has_location, 'runtime.file.location')
    check(isinstance(spec.loader, importlib.machinery.ExtensionFileLoader), 'runtime.file.loader')
    check(isinstance(module_file, str) and bool(module_file), 'runtime.file.attribute')
    check(pathlib.Path(spec.origin).is_absolute(), 'runtime.file.absolute')
    check(spec.loader.name == name, 'runtime.file.loader_name')
    try:
        binary = pathlib.Path(spec.origin).resolve(strict=True)
        check(stat.S_ISREG(binary.stat().st_mode), 'runtime.file.regular')
        check(pathlib.Path(module_file).resolve(strict=True) == binary, 'runtime.file.origin')
        check(pathlib.Path(spec.loader.get_filename(name)).resolve(strict=True) == binary,
              'runtime.file.loader_path')
        check(any(str(binary).endswith(s) for s in importlib.machinery.EXTENSION_SUFFIXES),
              'runtime.file.suffix')
        digest = sha(binary.read_bytes())
    except OSError as exc:
        raise Rejected('runtime.file.unavailable') from exc
    return dict(origin=spec.origin, binary_location=str(binary), file_present=True,
                binary_sha256=digest, identity_method='EXTENSION_SPEC_FILE_BYTES_SHA256')


def runtime_identity():
    """Report local byte identities without hostname calls or runtime-equivalence claims."""
    exe = pathlib.Path(sys.executable).resolve(strict=True)
    check(sys.modules.get('zlib') is zlib and importlib.util.find_spec('zlib') is zlib.__spec__,
          'runtime.zlib.loaded')
    binary = module_binary_identity(zlib, exe)
    return dict(protocol=PROTOCOL, schema='agicore:portable-runtime-identity:v9',
        python_version_info=list(sys.version_info), python_implementation=sys.implementation.name,
        sys_platform=sys.platform, python_executable=str(exe),
        python_executable_sha256=sha(exe.read_bytes()),
        zlib_compile_version=zlib.ZLIB_VERSION, zlib_runtime_version=zlib.ZLIB_RUNTIME_VERSION,
        zlib_module_origin=binary['origin'], zlib_file_present=binary['file_present'],
        zlib_binary_location=binary['binary_location'], zlib_binary_sha256=binary['binary_sha256'],
        zlib_binary_identity_method=binary['identity_method'],
        hostname=None, hostname_status='NOT_QUERIED_NON_AUTHORITATIVE_DIAGNOSTIC',
        source_sha256=sha(pathlib.Path(__file__).read_bytes()),
        original_runtime_equivalence='NOT_ESTABLISHED',
        production_runtime_identity_claimed=False, registered_profile_replaced=False)


def resource_snapshot():
    """Measure optional local memory; measurements never claim limit enforcement."""
    unavailable = dict(status='NOT_MEASURED', peak_working_set_bytes=None,
                       peak_commit_bytes=None, enforcement_claimed=False)
    try:
        if sys.platform == 'win32':
            import ctypes
            class Counters(ctypes.Structure):
                _fields_ = [('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong)] + [
                    (n, ctypes.c_size_t) for n in ('PeakWorkingSetSize', 'WorkingSetSize',
                    'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                    'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
            c = Counters()
            c.cb = ctypes.sizeof(c)
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel.GetCurrentProcess.restype = ctypes.c_void_p
            psapi = ctypes.WinDLL('psapi', use_last_error=True)
            psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
            if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(c), c.cb):
                raise ctypes.WinError(ctypes.get_last_error())
            return dict(status='MEASURED', peak_working_set_bytes=c.PeakWorkingSetSize,
                        peak_commit_bytes=c.PeakPagefileUsage, method='Windows GetProcessMemoryInfo',
                        enforcement_claimed=False)
        if sys.platform == 'linux':
            import resource
            return dict(status='MEASURED',
                        peak_working_set_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                        peak_commit_bytes=None, peak_commit_status='NOT_MEASURED',
                        method='Linux getrusage(RUSAGE_SELF).ru_maxrss KiB', enforcement_claimed=False)
        return dict(unavailable, reason='UNSUPPORTED_PLATFORM')
    except (ImportError, OSError, AttributeError, ValueError) as exc:
        return dict(unavailable, reason=type(exc).__name__+': '+str(exc))


def create_output_directory(parent):
    """Create a distinct child directory; archive names never become output paths."""
    root = pathlib.Path(parent).resolve()
    try:
        root.mkdir(parents=True, exist_ok=True)
        check(root.is_dir(), 'output.directory')
        return pathlib.Path(tempfile.mkdtemp(prefix='portable-verifier-', dir=root))
    except OSError as exc:
        raise Rejected('output.directory') from exc


def main(argv=None):
    """Verify explicit inputs; historical mode never substitutes repository test data."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--archive', type=pathlib.Path, help='Archive with separately supplied trust')
    mode.add_argument('--historical-archive', type=pathlib.Path,
                      help='Explicit original archive, checked against the frozen V2 contract')
    parser.add_argument('--trust', type=pathlib.Path)
    parser.add_argument('--output-root', type=pathlib.Path,
                        help='Optional parent for a new collision-safe supplemental receipt directory')
    args = parser.parse_args(argv)
    if bool(args.archive) != bool(args.trust):
        parser.error('--archive requires --trust; historical mode forbids --trust')
    start = time.perf_counter_ns()
    historical = args.historical_archive is not None
    if historical:
        trust = load_contract()['trust']
    else:
        with args.trust.open('rb') as f:
            trust = parse_json(f.read(MAX_ENTRY+1), 'trust', exact=False)
    path = args.historical_archive if historical else args.archive
    with path.open('rb') as f:
        raw = f.read(MAX_ARCHIVE+1)
    result = verify_archive(raw, trust)
    result.update(status=PASS if historical else 'PASS_PORTABLE_INTEGRITY_WITH_EXPLICIT_TRUST',
                  verification_mode='EXTERNAL_HISTORICAL_EVIDENCE_VERIFICATION' if historical else
                  'EXPLICIT_ARCHIVE_AND_TRUST',
                  precommitted_historical_contract_sha256=PLAN_SHA256 if historical else None,
                  runtime=runtime_identity(), resources=resource_snapshot(),
                  elapsed_ns=time.perf_counter_ns()-start, supplemental_evidence_only=True)
    if args.output_root is not None:
        directory = create_output_directory(args.output_root)
        result['receipt_directory'] = str(directory)
        with (directory/'portable-receipt.json').open('xb') as f:
            f.write(canonical(result))
    print(json.dumps(result,sort_keys=True,indent=2))
    return result


if __name__ == '__main__':
    try:
        main()
    except Rejected as failure:
        print(json.dumps(dict(status='BLOCKED_PORTABLE_DECODING' if failure.layer.startswith('shard.') else
              'BLOCKED_PORTABLE_ARCHIVE_INTEGRITY',layer=failure.layer,trace=failure.trace)))
        sys.exit(1)
