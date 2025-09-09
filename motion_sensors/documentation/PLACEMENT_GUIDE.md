# Motion Sensor Placement Guide

## Overview

This guide provides professional recommendations for optimal motion sensor placement based on Aeotec SmartThings Motion Sensor specifications and industry best practices.

## Sensor Specifications

### Aeotec SmartThings Motion Sensor
- **Detection Technology**: PIR (Passive Infrared)
- **Field of View**: 120° horizontal, 110° vertical
- **Detection Range**: Up to 5 meters (16 feet)
- **Mounting Height**: 2-2.5 meters (6-8 feet) recommended
- **Response Time**: 1 second detection, 3 second cooldown
- **Power**: CR2 3V Lithium battery (2-3 year life)
- **Connectivity**: Z-Wave Plus (908.42 MHz)

## General Placement Principles

### 1. Height Positioning
```
Optimal Heights:
├── 2.2 meters (7.2 feet) - Standard ceiling mount
├── 2.4 meters (7.9 feet) - High ceiling mount
└── 2.0 meters (6.6 feet) - Minimum effective height

Avoid:
├── Below 1.8 meters - Reduced detection range
├── Above 2.5 meters - Detection dead zones
└── Uneven heights - Coverage gaps
```

### 2. Orientation Strategy
```
120° Coverage Optimization:
├── Corner Placement - Maximum room coverage
├── Wall Mount (2/3 height) - Traffic pattern focus  
├── Ceiling Mount - Central area coverage
└── Doorway Mount - Entry/exit monitoring
```

### 3. Environmental Considerations
```
Avoid Placement Near:
├── Heat Sources (vents, radiators, fireplaces)
├── Direct Sunlight (windows, skylights)
├── Moving Objects (fans, plants, curtains)
├── Reflective Surfaces (mirrors, metal surfaces)
└── Electrical Interference (WiFi routers, microwaves)
```

## Room-Specific Placement

### Living Room
```
Primary Sensor: M01_LivingRoom_Main
├── Position: Corner at 2.2m height
├── Orientation: 225° (diagonal into room)
├── Coverage: Main seating area + entrance
├── Priority: High
└── Zone: 5m radius from corner

Secondary Sensor: M02_LivingRoom_TV
├── Position: Opposite corner at 2.2m height  
├── Orientation: 180° (toward TV wall)
├── Coverage: Entertainment area
├── Priority: Medium
└── Zone: Overlap with primary for seamless coverage
```

**Optimal Coordinates:**
- Primary: (3.5, 4.0, 2.2) facing 225°
- Secondary: (1.0, 6.0, 2.2) facing 180°

### Kitchen
```
Primary Sensor: M03_Kitchen_Main
├── Position: Above prep area at 2.3m height
├── Orientation: 270° (toward counter/stove)
├── Coverage: Cooking and prep zones
├── Priority: High
└── Zone: Work triangle coverage

Secondary Sensor: M04_Kitchen_Dining  
├── Position: Above dining area at 2.2m height
├── Orientation: 90° (toward dining table)
├── Coverage: Eating and socializing area
├── Priority: Medium
└── Zone: Dining table and chairs
```

**Optimal Coordinates:**
- Primary: (-1.5, 5.5, 2.3) facing 270°
- Secondary: (-0.5, 3.5, 2.2) facing 90°

### Master Bedroom
```
Single Sensor: M05_Bedroom_Master
├── Position: Corner opposite bed at 2.2m height
├── Orientation: 315° (toward bed and entrance)
├── Coverage: Bed area + doorway
├── Priority: High
└── Zone: Complete bedroom coverage

Privacy Considerations:
├── Avoid direct bed monitoring angle
├── Focus on movement patterns, not stationary positions
├── Position to detect entry/exit primarily
└── Consider smart scheduling for sleep hours
```

**Optimal Coordinates:**
- Position: (4.5, -1.5, 2.2) facing 315°

### Hallway
```
Primary Sensor: M06_Hallway_Central
├── Position: Central ceiling mount at 2.4m height
├── Orientation: 0° (down main corridor)
├── Coverage: Primary traffic flow
├── Priority: Critical
└── Zone: Full hallway length

Secondary Sensor: M07_Hallway_Rooms
├── Position: Secondary corridor at 2.4m height
├── Orientation: 180° (toward room entrances)  
├── Coverage: Room access points
├── Priority: High
└── Zone: Bedroom wing corridor
```

**Optimal Coordinates:**
- Primary: (0.5, 0.5, 2.4) facing 0°
- Secondary: (-0.5, -0.5, 2.4) facing 180°

### Bathroom
```
Privacy-Focused Sensor: M08_Bathroom_Main
├── Position: Near entrance at 2.1m height
├── Orientation: 135° (toward vanity/entrance only)
├── Coverage: Entry and vanity area
├── Priority: Medium
└── Zone: Respect privacy boundaries

Privacy Guidelines:
├── Never monitor shower/toilet directly
├── Focus on occupancy detection only
├── Consider smart shutoff during private times
└── Position for safety (fall detection) vs surveillance
```

**Optimal Coordinates:**
- Position: (-2.5, -0.5, 2.1) facing 135°

### Entry/Foyer
```
Security Sensor: M10_Entry_Main
├── Position: High mount at 2.5m height
├── Orientation: 0° (toward front door)
├── Coverage: Main entrance monitoring
├── Priority: Critical
└── Zone: Entry security perimeter

Security Features:
├── First detection point for visitors
├── Integration with door locks/cameras
├── Immediate notification priority
└── Backup power consideration
```

**Optimal Coordinates:**
- Position: (1.0, 2.0, 2.5) facing 0°

## Advanced Placement Strategies

### 1. Overlap Zone Management
```
Seamless Coverage Strategy:
├── 10-15% overlap between adjacent sensors
├── Eliminate dead zones at boundaries
├── Coordinate cooldown periods to prevent gaps
└── Test actual coverage with Actor movement
```

### 2. Multi-Level Coverage
```
Vertical Coverage Zones:
├── Upper Zone (2.0-2.5m): Standard PIR detection
├── Lower Zone (1.5-2.0m): Pet immunity consideration
├── Floor Zone (0-1.5m): Fallen person detection
└── Ceiling Zone (2.5m+): Avoid mounting too high
```

### 3. Traffic Pattern Analysis
```
Movement Flow Optimization:
├── Primary Paths: Kitchen ↔ Living Room ↔ Hallway
├── Secondary Paths: Bedroom ↔ Bathroom ↔ Hallway  
├── Entry Points: Front door → Foyer → Living areas
└── Service Areas: Utility → Kitchen, Garage → Entry
```

## Coverage Validation

### 1. Physical Testing
```bash
# Blender BGE Testing
1. Load motion sensor demo script
2. Move Actor through all rooms systematically
3. Verify detection events in each zone
4. Check for dead zones or missed areas
5. Adjust sensor positions as needed
```

### 2. Coverage Heat Map
```python
# Generate coverage visualization
from motion_sensors.demos import show_detection_zones

# Shows each sensor's 5m radius, 120° FOV coverage area
show_detection_zones()
```

### 3. Performance Metrics
```
Validation Criteria:
├── 100% room coverage (no blind spots)
├── <1 second detection latency
├── 3 second cooldown respected
├── No false positives from environmental factors
└── Smooth handoff between sensors
```

## Troubleshooting Common Issues

### 1. Dead Zones
```
Problem: Areas with no sensor coverage
Solutions:
├── Add additional sensors in blind spots
├── Reposition existing sensors for better angles
├── Use higher mounting positions
└── Consider corner vs wall mounting
```

### 2. False Positives
```
Problem: Sensors triggering without human presence
Causes & Solutions:
├── Heat Sources → Move sensor away from vents/heaters
├── Sunlight → Add shade or reposition sensor
├── Moving Objects → Secure curtains, plants, decorations
└── Pets → Adjust sensitivity or mounting height
```

### 3. Poor Detection Range
```
Problem: Sensors not detecting at expected 5m range
Solutions:
├── Check mounting height (optimal 2.2m)
├── Verify sensor orientation
├── Remove obstructions in detection path
└── Test with fresh batteries
```

### 4. Coverage Gaps
```
Problem: Movement not detected between sensors
Solutions:
├── Increase overlap zones
├── Add transitional sensors
├── Coordinate cooldown timing
└── Use higher sensor density in critical areas
```

## Professional Installation Notes

### 1. Mounting Hardware
```
Recommended Mounting:
├── Wall Bracket: Adjustable angle mount
├── Ceiling Mount: Fixed downward angle
├── Corner Mount: 45° bracket for optimal coverage
└── Magnetic Mount: Temporary/testing only
```

### 2. Wire Management
```
For Wired Sensors (if applicable):
├── Concealed wiring through walls/ceiling
├── Power over Ethernet (PoE) consideration
├── Backup battery integration
└── Service access maintenance
```

### 3. Integration Testing
```
Post-Installation Validation:
├── Test each sensor individually
├── Verify SmartThings app connectivity
├── Test overlap zones and handoffs
├── Document sensor IDs and locations
└── Create maintenance schedule
```

This placement guide ensures optimal motion sensor coverage for both security and automation purposes while respecting privacy and maintaining professional installation standards.
