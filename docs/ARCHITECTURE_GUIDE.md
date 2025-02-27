# ax-devil-device-api Architecture Guide

## Overview

The ax-devil-device-api is built on a three-layer architecture that clearly separates responsibilities and supports long-term adaptability. This guide provides an overview of the architecture and links to detailed documentation for each layer.

## Three-Layer Architecture

### Layer 1: Communications Layer
The foundational layer that handles all low-level network communication, authentication, and protocol details. This layer is designed to be stable and unchanging once mature.

[Working with Layer 1](WORKING_WITH_LAYER_1.md)

### Layer 2: Feature Layer
The dynamic layer where new device functionalities are developed as independent modules. Each module is dedicated to specific device capabilities.
- Functionality abstraction, provide an interface such as 'get device info'. Abstract the actual request to the device.
- One of the two user facing layers. This layer provides modules that users can interact with trough the client.

[Working with Layer 2](WORKING_WITH_LAYER_2.md)

### Layer 3: Interface Layer
- Provide examples of how to use the library.
- On of the two user facing layers. This layer is used to create command line tools and other examples of how to use the library.

[Working with Layer 3](WORKING_WITH_LAYER_3.md)