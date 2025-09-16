# Enhanced MCP Camera Service Guide

## Overview
The camera service now provides intelligent camera selection tools for VLM agents, allowing them to choose between bird-eye and first-person views based on context.

## Available MCP Tools

### 1. Camera Capture Tools
- **`capture_bird_eye_view()`** - Top-down spatial overview for navigation
- **`capture_first_person_view()`** - Actor's eye-level view for detailed interaction

### 2. Camera Intelligence Tools
- **`get_camera_recommendations()`** - AI-driven camera selection based on task context
- **`get_available_cameras()`** - List all cameras in the scene
- **`get_camera_info()`** - Detailed information about specific cameras

### 3. Management Tools
- **`list_camera_captures()`** - Browse captured screenshots
- **`camera_service_health()`** - Service status and diagnostics

## Intelligent Camera Selection

### When to Use Bird-Eye View
- Navigation tasks ("go to", "move to", "find room")
- Getting unstuck or reorienting
- Path planning and spatial understanding
- Room layout comprehension

### When to Use First-Person View
- Object interaction ("use", "operate", "cook")
- Reading details, labels, or signs
- Precise positioning and manipulation
- Understanding what's directly accessible

## Usage Flow for VLM Agents

1. **Get Recommendations**: Call `get_camera_recommendations()` with current task context
2. **Capture View**: Use recommended camera tool (`capture_bird_eye_view()` or `capture_first_person_view()`)
3. **Process Image**: Analyze captured screenshot for decision making
4. **Switch as Needed**: VLM can call different camera tools based on changing context

## Key Benefits

- **No Simultaneous Capture Required**: BGE limitation handled gracefully
- **Context-Aware Selection**: Intelligent recommendations based on task requirements
- **Seamless Integration**: MCP tools work naturally with VLM workflows
- **Fallback Safety**: Default to bird-eye view for navigation tasks

## Architecture Notes

- BGE allows only one active camera for `makeScreenshot()` at a time
- Sequential capture via MCP tools is more elegant than simultaneous attempts
- VLM agent can intelligently choose which camera tool to call
- Each camera type has distinct use cases and optimal scenarios
