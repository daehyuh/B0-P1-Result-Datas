"""Syntax extraction only. Candidate edges never imply runtime reachability."""

import json
from collections import defaultdict

import tree_sitter_java
from tree_sitter import Language, Parser

from .storage import digest

VERSION = "java-syntax-v3-ts0.25-java0.23"
CLASS_KINDS = {
    "class_declaration",
    "interface_declaration",
    "enum_declaration",
    "record_declaration",
    "annotation_type_declaration",
}
CALLABLE_KINDS = {
    "method_declaration",
    "constructor_declaration",
    "compact_constructor_declaration",
}
ROUTES = {
    "GetMapping": "GET",
    "PostMapping": "POST",
    "PutMapping": "PUT",
    "DeleteMapping": "DELETE",
    "PatchMapping": "PATCH",
    "RequestMapping": "ANY",
}
GUARDS = {"PreAuthorize", "PostAuthorize", "Secured", "RolesAllowed"}
INPUTS = {"PathVariable", "RequestParam", "RequestBody", "RequestHeader", "CookieValue"}
ROLE_NAMES = {
    "exec": "process",
    "start": "process",
    "execute": "sql_or_process",
    "executeQuery": "sql",
    "query": "sql",
    "openConnection": "network",
    "send": "network",
    "readObject": "deserialization",
    "readAllBytes": "file",
    "write": "output",
    "flush": "output",
    "sendRedirect": "redirect",
    "checkPermission": "guard",
    "hasRole": "guard",
    "isAuthorized": "guard",
}


def walk(node):
    yield node
    for child in node.named_children:
        yield from walk(child)


def text(node):
    return node.text.decode("utf-8") if node else ""


def field(node, name):
    return node.child_by_field_name(name)


def annotations(node):
    modifiers = next((n for n in node.named_children if n.type == "modifiers"), None)
    result = []
    for item in modifiers.named_children if modifiers else []:
        if item.type not in {"annotation", "marker_annotation"}:
            continue
        values = {}
        arguments = field(item, "arguments")
        if arguments:
            for arg in arguments.named_children:
                key = text(field(arg, "key")) if arg.type == "element_value_pair" else "value"
                value = field(arg, "value") if arg.type == "element_value_pair" else arg
                # Only literal strings are interpreted; constants remain explicitly unresolved.
                strings = []
                for leaf in walk(value):
                    if leaf.type == "string_literal":
                        try:
                            strings.append(json.loads(text(leaf)))
                        except json.JSONDecodeError:
                            pass
                values[key] = {
                    "strings": strings,
                    "expression": text(value),
                    "literal": value.type in {"string_literal", "element_value_array_initializer"},
                }
        result.append(
            {
                "name": text(field(item, "name")),
                "text": text(item),
                "values": values,
                "line": item.start_point.row + 1,
            }
        )
    return result


def extract(path, content):
    parser = Parser(Language(tree_sitter_java.language()))
    tree = parser.parse(content)
    root = tree.root_node
    package = ""
    imports = []
    for item in root.named_children:
        if item.type == "package_declaration":
            package = text(item).removeprefix("package").strip().rstrip(";")
        if item.type == "import_declaration":
            imports.append(text(item).removeprefix("import").strip().rstrip(";"))
    symbols, calls, facts = [], [], []

    def sid(node, kind, name):
        return digest([path, node.start_byte, node.end_byte, kind, name])[:24]

    def add_fact(kind, symbol, node, details):
        facts.append(
            {
                "id": digest([path, symbol["id"], node.start_byte, kind, details])[:24],
                "symbol_id": symbol["id"],
                "path": path,
                "kind": kind,
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
                "status": "candidate",
                "provenance": VERSION,
                **details,
            }
        )

    def visit(node, owner=None, method=None):
        current_owner, current_method = owner, method
        if node.type in CLASS_KINDS | CALLABLE_KINDS:
            name = text(field(node, "name"))
            kind = (
                "class"
                if node.type in CLASS_KINDS
                else ("constructor" if "constructor" in node.type else "method")
            )
            qualified = ".".join(
                filter(None, [owner["qualified_name"] if owner else package, name])
            )
            body = field(node, "body")
            signature = (
                content[node.start_byte : body.start_byte if body else node.end_byte]
                .decode()
                .strip()
            )
            parameters = field(node, "parameters")
            params = []
            for param in parameters.named_children if parameters else []:
                if param.type in {"formal_parameter", "spread_parameter"}:
                    params.append(
                        {
                            "name": text(field(param, "name")),
                            "type": text(field(param, "type")),
                            "annotations": annotations(param),
                        }
                    )
            symbol = {
                "id": sid(node, kind, name),
                "path": path,
                "kind": kind,
                "name": name,
                "qualified_name": qualified,
                "owner_id": owner["id"] if owner else None,
                "signature": signature,
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
                "annotations": annotations(node),
                "parameters": params,
                "return_type": text(field(node, "type")),
                "package": package,
                "imports": imports,
                "provenance": VERSION,
                "bases": [],
                "locals": {},
            }
            if kind == "class":
                for key, relation in [
                    ("superclass", "EXTENDS"),
                    ("interfaces", "IMPLEMENTS"),
                    ("extends_interfaces", "EXTENDS"),
                ]:
                    parent = field(node, key)
                    if not parent and key == "extends_interfaces":
                        parent = next(
                            (n for n in node.named_children if n.type == "extends_interfaces"), None
                        )
                    if parent:
                        identifiers = [
                            text(n)
                            for n in walk(parent)
                            if n.type in {"type_identifier", "scoped_type_identifier"}
                            and n.parent.type not in {"type_arguments", "scoped_type_identifier"}
                        ]
                        symbol["bases"].extend({"type": t, "kind": relation} for t in identifiers)
                current_owner, current_method = symbol, None
            else:
                current_method = symbol
                if body:
                    for local in walk(body):
                        if local.type == "local_variable_declaration":
                            for dec in local.named_children:
                                if dec.type == "variable_declarator":
                                    symbol["locals"][text(field(dec, "name"))] = text(
                                        field(local, "type")
                                    )
            symbols.append(symbol)
            for ann in symbol["annotations"]:
                short = ann["name"].split(".")[-1]
                if short in ROUTES:
                    bases = []
                    for base_ann in owner["annotations"] if owner and kind != "class" else []:
                        if base_ann["name"].split(".")[-1] == "RequestMapping":
                            bases.extend(
                                base_ann["values"]
                                .get("path", base_ann["values"].get("value", {}))
                                .get("strings", [])
                            )
                    value = ann["values"].get("path", ann["values"].get("value", {}))
                    routes = value.get("strings", [])
                    paths = [
                        "/" + (a.strip("/") + "/" + b.strip("/")).strip("/")
                        for a in (bases or [""])
                        for b in (routes or [""])
                    ]
                    add_fact(
                        "route",
                        symbol,
                        node,
                        {
                            "http_method": ROUTES[short],
                            "paths": paths,
                            "annotation": ann["text"],
                            "path_resolution": "literal"
                            if not ann["values"] or value.get("literal")
                            else "unresolved",
                            "note": "Annotation-name match; runtime mapping and profiles unverified",
                        },
                    )
                if short in GUARDS:
                    add_fact(
                        "guard",
                        symbol,
                        node,
                        {
                            "annotation": ann["text"],
                            "note": "Method-security activation and actual enforcement unverified",
                        },
                    )
                if short in {"Test", "ParameterizedTest", "RepeatedTest"}:
                    add_fact("test", symbol, node, {"annotation": ann["text"]})
                if short in {"Configuration", "EnableWebSecurity", "EnableMethodSecurity", "Bean"}:
                    add_fact("configuration", symbol, node, {"annotation": ann["text"]})
            for param in params:
                for ann in param["annotations"]:
                    if ann["name"].split(".")[-1] in INPUTS:
                        add_fact(
                            "input",
                            symbol,
                            node,
                            {"parameter": param["name"], "annotation": ann["text"]},
                        )
        elif node.type == "field_declaration" and owner:
            for dec in node.named_children:
                if dec.type == "variable_declarator":
                    name = text(field(dec, "name"))
                    symbol = {
                        "id": sid(dec, "field", name),
                        "path": path,
                        "kind": "field",
                        "name": name,
                        "qualified_name": owner["qualified_name"] + "." + name,
                        "owner_id": owner["id"],
                        "signature": text(node),
                        "start_line": node.start_point.row + 1,
                        "end_line": node.end_point.row + 1,
                        "type": text(field(node, "type")),
                        "annotations": annotations(node),
                        "provenance": VERSION,
                    }
                    symbols.append(symbol)
                    for ann in symbol["annotations"]:
                        if ann["name"].split(".")[-1] in {
                            "Autowired",
                            "Inject",
                            "Resource",
                            "Value",
                        }:
                            add_fact(
                                "injection",
                                symbol,
                                node,
                                {"annotation": ann["text"], "declared_type": symbol["type"]},
                            )
        elif node.type in {"method_invocation", "object_creation_expression"} and method:
            args = field(node, "arguments")
            name = text(field(node, "name") or field(node, "type"))
            call = {
                "id": sid(node, "call", name),
                "caller_id": method["id"],
                "path": path,
                "start_line": node.start_point.row + 1,
                "end_line": node.end_point.row + 1,
                "column": node.start_point.column,
                "name": name,
                "receiver": text(field(node, "object")),
                "expression": text(node),
                "arguments": [text(a) for a in args.named_children] if args else [],
                "kind": "constructor" if node.type == "object_creation_expression" else "method",
                "status": "unresolved",
                "targets": [],
                "provenance": VERSION,
            }
            calls.append(call)
            if name in ROLE_NAMES:
                add_fact(
                    "security_call",
                    method,
                    node,
                    {
                        "category": ROLE_NAMES[name],
                        "call_id": call["id"],
                        "expression": text(node),
                        "note": "Name-based navigation hint, not a verified API or vulnerability",
                    },
                )
        for child in node.named_children:
            visit(child, current_owner, current_method)

    visit(root)
    return {
        "symbols": symbols,
        "calls": calls,
        "facts": facts,
        "parse_error": root.has_error,
        "package": package,
        "imports": imports,
    }


def link(parsed_files, checkpoint=lambda: None, on_progress=None):
    symbols = [s for p in parsed_files for s in p["symbols"]]
    calls = [c for p in parsed_files for c in p["calls"]]
    by_id = {s["id"]: s for s in symbols}
    classes = [s for s in symbols if s["kind"] == "class"]
    methods = [s for s in symbols if s["kind"] in {"method", "constructor"}]
    edges = []
    class_by_name = defaultdict(list)
    methods_by_owner = defaultdict(list)
    method_lookup = defaultdict(list)
    fields_by_owner = defaultdict(dict)
    edge_ids = set()
    for cls in classes:
        class_by_name[cls["qualified_name"]].append(cls)
    for method in methods:
        methods_by_owner[method["owner_id"]].append(method)
        method_lookup[
            (method["owner_id"], method["name"], method["kind"], len(method.get("parameters", [])))
        ].append(method)
    for symbol in symbols:
        if symbol["kind"] == "field":
            fields_by_owner[symbol["owner_id"]][symbol["name"]] = symbol.get("type", "")

    def add_edge(src, dst, kind, evidence, status="candidate"):
        edge_id = digest([src, dst, kind, evidence])[:24]
        if edge_id in edge_ids:
            return
        edge_ids.add(edge_id)
        edges.append(
            {
                "id": edge_id,
                "src_id": src,
                "dst_id": dst,
                "kind": kind,
                "status": status,
                "evidence": evidence,
                "provenance": VERSION,
            }
        )

    def type_candidates(type_name, context):
        base = type_name.split("<")[0].strip().removesuffix("[]")
        if not base:
            return []
        names = {base, context.get("package", "") + "." + base}
        names.update(i for i in context.get("imports", []) if i.endswith("." + base))
        names.update(i[:-1] + base for i in context.get("imports", []) if i.endswith(".*"))
        return [c for name in sorted(names) for c in class_by_name.get(name, [])]

    progress_total = len(symbols) + len(calls)
    for current, s in enumerate(symbols, start=1):
        checkpoint()
        if on_progress:
            on_progress(current, progress_total, s["path"])
        if s.get("owner_id"):
            add_edge(
                s["owner_id"],
                s["id"],
                "CONTAINS",
                {"path": s["path"], "start_line": s["start_line"]},
                "syntax",
            )
        for base in s.get("bases", []):
            for target in type_candidates(base["type"], s):
                add_edge(
                    s["id"],
                    target["id"],
                    base["kind"],
                    {"path": s["path"], "start_line": s["start_line"]},
                )

    for current, call in enumerate(calls, start=len(symbols) + 1):
        checkpoint()
        if on_progress:
            on_progress(current, progress_total, call["path"])
        method = by_id[call["caller_id"]]
        owner = by_id.get(method["owner_id"])
        target_classes = []
        if call["kind"] == "constructor":
            target_classes = type_candidates(call["name"], method)
        elif owner and call["receiver"] in {"", "this"}:
            target_classes = [owner]
        elif owner:
            receiver = call["receiver"].removeprefix("this.")
            bindings = dict(fields_by_owner[owner["id"]])
            bindings.update({p["name"]: p["type"] for p in method.get("parameters", [])})
            bindings.update(method.get("locals", {}))
            target_classes = type_candidates(bindings.get(receiver, receiver), method)
        targets = [
            m
            for cls in target_classes
            for m in method_lookup.get(
                (cls["id"], call["name"], call["kind"], len(call["arguments"])), []
            )
        ]
        call["targets"] = [t["id"] for t in targets]
        call["status"] = "candidate" if targets else "unresolved"
        for target in targets:
            add_edge(
                method["id"],
                target["id"],
                "CALLS",
                {"path": call["path"], "start_line": call["start_line"], "call_id": call["id"]},
            )

    inheritance = [e for e in edges if e["kind"] in {"EXTENDS", "IMPLEMENTS"}]
    for edge in inheritance:
        checkpoint()
        for child in methods_by_owner[edge["src_id"]]:
            for parent in methods_by_owner[edge["dst_id"]]:
                if parent["name"] == child["name"] and [
                    p["type"] for p in parent["parameters"]
                ] == [p["type"] for p in child["parameters"]]:
                    add_edge(
                        child["id"],
                        parent["id"],
                        "OVERRIDES",
                        {"path": child["path"], "start_line": child["start_line"]},
                    )
    return symbols, calls, edges
