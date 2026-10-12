"""Sans-IO protocol families. Importing this package registers every binding."""

from . import cgi, dca, jsonrpc, rest, service_json, soap  # noqa: F401  (registration side effects)
