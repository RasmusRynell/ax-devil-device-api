# ax-devil-device-api: Axis Development Utilities - Device API

## Current Overall Architecture

### Layer 1: Communications Layer
- **Core Components:**
  - `DeviceClient`: Centralized client managing device communication and session handling
    - Advanced connection pooling via requests.Session
    - Persistent connection management
    - Automatic SSL/TLS session reuse
    - Cookie persistence across requests
    - Configurable pool sizes and timeouts
    - Session lifecycle management
    - Thread-safe request handling
    - Support for temporary sessions
  - `Response[T]`: Type-safe response wrapper with comprehensive error handling
  - `TransportResponse`: Low-level HTTP response encapsulation
  - `DeviceEndpoint`: Structured API endpoint definitions
  - `AuthHandler`: Unified authentication handling with method auto-detection
  - `ProtocolHandler`: Protocol-specific connection logic and SSL/TLS handling
  - `DeviceConfig`: Comprehensive configuration management
    - Connection parameters
    - Authentication settings
    - Protocol selection
    - SSL/TLS configuration
  - `SSLConfig`: Dedicated SSL/TLS configuration
    - Certificate verification
    - Client certificates
    - Certificate pinning
    - Custom CA support

### Layer 2: Feature Modules
- **Base Architecture:**
  - `FeatureClient`: Base class providing common feature functionality
  - `FeatureResponse`: Standardized response handling for features
  - Strong typing and validation patterns
  - Modular error handling system
  - Feature-specific data models
  - Comprehensive validation mechanisms
  
- **Implemented Features:**
  - `DeviceInfoClient`: Core device management and configuration
    - Device information retrieval
    - Health monitoring
    - System restart capabilities
    - Hardware identification
  
  - `NetworkClient`: Network settings and connectivity
    - Interface configuration
    - Network status monitoring
    - IP configuration management
    - Link status and metrics
  
  - `MediaClient`: Media streaming and snapshot capabilities
    - JPEG snapshot capture
    - Resolution control
    - Compression settings
    - Image rotation
  
  - `MqttClient`: MQTT protocol integration
    - Broker configuration
    - Connection management
    - Client lifecycle
    - Topic management
  
  - `GeoCoordinatesClient`: Location and positioning features
    - Geographic coordinates
    - Device orientation
    - Installation parameters
    - Position updates
  
  - `AnalyticsMqttClient`: Analytics data via MQTT protocol
    - Data source management
    - Publisher configuration
    - Data stream control
    - Analytics event handling
    
  - `FeatureFlagClient`: Dynamic feature management
    - Feature flag configuration
    - Flag state retrieval
    - Batch flag operations
    - API version management

### Layer 3: Interface Layer
- **Main Client Interface:**
  - Context manager support for proper resource cleanup
  - Session management controls
    - Persistent session handling
    - Temporary session creation
    - Session state clearing
  - Lazy-loaded feature clients
  - Thread-safe operations
  - Resource cleanup guarantees

- **CLI Framework:**
  - **Core Components:**
    - Common CLI utilities (`cli_core.py`)
    - Unified error handling and formatting
    - Environment variable support
    - Debug mode capabilities
    - Interactive confirmations
  
  - **Command Structure:**
    - Feature-specific CLI modules
    - Consistent command patterns
    - Type-safe parameter handling
    - Command documentation
  
  - **Configuration Management:**
    - Environment-based configuration
    - Command-line overrides
    - Configuration validation
    - Secure credential handling
  
  - **Security Features:**
    - Protocol auto-negotiation
    - HTTP/HTTPS fallback mechanisms
    - SSL certificate handling
    - Secure credential input
  
  - **Error Handling:**
    - Structured error reporting
    - User-friendly error messages
    - Debug information support
    - Error recovery strategies

