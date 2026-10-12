"""Sans-IO protocol families. Importing this package registers every binding."""

from . import cgi, dca, jsonrpc  # noqa: F401  (registration side effects)
