# ax-devil-device-api: Axis Device Development Utilities

## Vision Statement
ax-devil-device-api is a Python library for working with Axis device APIs. It focuses on making device interactions reliable and predictable through type safety and error handling. The goal is to provide an interface that makes sense for real-world device management.

## Core Architecture & Philosophy
The library is built around a simple idea: make Axis device APIs easier to work with in Python while keeping things maintainable. It uses a three-layer architecture to separate the core communication, device features, and user interfaces, making it easier to add new features or fix issues when APIs change.

## Project Overview
ax-devil-device-api is built on a foundational principle: to create a robust, stable system for managing common device interactions while allowing unlimited extensibility via feature-specific modules. Its three-layer architecture clearly separates responsibilities and supports long-term adaptability.

### Layer 1: Communications Layer
- **Fundamental & Stable:**  
  This layer supplies the essential device communication infrastructure—serving as the system's unchanging bedrock once mature.
- **Responsibilities:**
  - **Network Protocols & Connectivity:** Manages HTTP, HTTPS to ensure reliable communication.
  - **Authentication & Security:** Basic authentication, SSL/TLS connections, and other key security measures.
  - **Transport Abstraction:** Provides a thin, immutable wrapper around HTTP responses that encapsulates transport-level success/failure states.
  - **Error Boundaries:** Captures and isolates transport-level failures (connection, SSL, timeout) without leaking implementation details.
  - **Raw Data Access:** Ensures Layer 2 has direct access to raw HTTP response data when needed, while maintaining clean transport-level abstractions.

### Layer 2: Feature Layer
- **Extension & Evolution:**  
  This dynamic layer is where new device functionalities are developed as independent modules, each dedicated to specific device capabilities.
- **Responsibilities:**
  - **Functionality Abstraction:** Implements device operations (e.g., retrieving device info, restarting devices, managing settings) using the communications layer.
  - **Data Normalization:** Parses and converts raw responses from Layer 1 into standardized, structured formats (like dictionaries or custom objects).
  - **Error Abstraction:** Translates low-level errors from the communications layer into intuitive, high-level exceptions.
  - **Modularity:** Allows new features to be integrated seamlessly without disrupting the core system, ensuring ongoing adaptability.

### Layer 3: Interface Layer
- **User-Facing Interaction & Examples:**  
  This layer provides front-end interfaces. A CLI offers quick operations and clear usage examples, while programmatic interfaces let users integrate the library directly into Python applications.
- **Responsibilities:**
  - **CLI & Demonstrative Interfaces:** Supplies simple, intuitive commands that map directly to the feature modules.
  - **Readable Output:** Formats and displays results in a human-friendly manner, even when responses are complex.
  - **Alternative Implementations:** While a CLI is the default, the design supports other interfaces to suit different workflows.

By clearly separating these three layers, ax-devil-device-api ensures:
- **Stability:** Layer 1 (Communications Layer) remains a solid, unchanging foundation.
- **Extensibility:** Layer 2 (Feature Layer) allows new features to be easily added without disrupting core operations.
- **Flexibility:** Layer 3 (Interface Layer) provides practical examples and multiple modes of interaction, whether via CLI or direct programmatic integration.
