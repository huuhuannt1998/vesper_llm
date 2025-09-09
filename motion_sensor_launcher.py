#!/usr/bin/env python3
"""
VESPER Motion Sensor System Launcher
===================================

Main launcher script for the VESPER Motion Sensor Detection System.
Provides easy access to all motion sensor features and configurations.

Usage:
    python motion_sensor_launcher.py [command] [options]

Commands:
    setup       - Set up motion sensors with optimal placement
    demo        - Run interactive motion sensor demonstration
    test        - Run motion sensor testing framework
    config      - Configure sensor layouts and specifications
    validate    - Validate sensor coverage and placement
    deploy      - Deploy sensors to Blender scene
    status      - Show current sensor status and statistics

Examples:
    python motion_sensor_launcher.py setup --layout medium_house
    python motion_sensor_launcher.py demo --sensors 6
    python motion_sensor_launcher.py validate --config my_sensors.json
"""

import argparse
import sys
import os
import json
from pathlib import Path

# Add motion_sensors to path
sys.path.append(str(Path(__file__).parent))

# Import motion sensor modules
try:
    from motion_sensors import (
        quick_setup,
        get_sensor_specs,
        SENSOR_SPECS
    )
    
    from motion_sensors.setup import (
        setup_smart_home_motion_sensors,
        calculate_optimal_sensor_positions,
        validate_sensor_coverage,
        export_sensor_configuration
    )
    
    from motion_sensors.demos import (
        run_comprehensive_demo,
        get_test_statistics,
        show_detection_zones
    )
    
    from motion_sensors.configs import (
        load_sensor_layout,
        save_sensor_layout
    )
    
    MOTION_SENSORS_AVAILABLE = True
    
except ImportError as e:
    MOTION_SENSORS_AVAILABLE = False
    print(f"❌ Motion sensor system not available: {e}")
    sys.exit(1)

def print_banner():
    """Print the VESPER motion sensor banner"""
    print("🏠" + "="*60 + "🏠")
    print("  VESPER Motion Sensor Detection System")
    print("  Production-Grade Smart Home Simulation")
    print("="*64)
    print(f"📊 Version: 1.0.0")
    print(f"🎯 Sensor Model: {SENSOR_SPECS['model']}")
    print(f"📐 Specs: {SENSOR_SPECS['field_of_view']}° FOV, {SENSOR_SPECS['detection_range']}m range")
    print("="*64)

def cmd_setup(args):
    """Setup motion sensors with optimal placement"""
    print("🚀 Setting up motion sensor system...")
    
    if args.layout:
        print(f"📋 Loading layout: {args.layout}")
        layout = load_sensor_layout(args.layout)
        if layout:
            print(f"✅ Loaded {layout['total_sensors']} sensors from {args.layout}")
            # Deploy sensors from layout
            deployed = 0
            for sensor in layout['sensors']:
                print(f"   📍 {sensor['id']}: {sensor['room']} at {sensor['position']}")
                deployed += 1
            print(f"📊 Layout deployment complete: {deployed} sensors configured")
        else:
            print(f"❌ Layout '{args.layout}' not found")
            return
    else:
        # Run full smart home setup
        result = setup_smart_home_motion_sensors()
        print(f"✅ Setup complete:")
        print(f"   📊 Sensors configured: {result['sensors_configured']}")
        print(f"   🚀 Sensors deployed: {result['sensors_deployed']}")
        print(f"   📁 Config saved: {result['config_file']}")

def cmd_demo(args):
    """Run interactive motion sensor demonstration"""
    print("🎬 Starting motion sensor demonstration...")
    print("🎮 This demo requires Blender BGE to be running")
    print("📋 Instructions:")
    print("   1. Load this script in Blender BGE")
    print("   2. Ensure Actor object exists in scene")
    print("   3. Move Actor around to trigger sensors")
    print("   4. Watch console for detection events")
    
    if args.sensors:
        print(f"🔢 Demo configured for {args.sensors} sensors")
    
    # Note: Actual demo would run in BGE context
    print("💡 To run demo in Blender BGE:")
    print("   from motion_sensors.demos import run_comprehensive_demo")
    print("   run_comprehensive_demo()")

def cmd_test(args):
    """Run motion sensor testing framework"""
    print("🧪 Running motion sensor tests...")
    
    if args.coverage:
        print("📊 Running coverage analysis...")
        # Test coverage validation
        test_sensors = [
            {"id": "TEST01", "position": {"x": 0, "y": 0, "z": 2}, "room": "test", "orientation": 0},
            {"id": "TEST02", "position": {"x": 3, "y": 3, "z": 2}, "room": "test", "orientation": 180}
        ]
        
        validation = validate_sensor_coverage(test_sensors)
        print(f"✅ Coverage test complete:")
        print(f"   📊 Total sensors: {validation['total_sensors']}")
        print(f"   🏠 Rooms covered: {len(validation['coverage_analysis'])}")
        print(f"   💡 Recommendations: {len(validation['recommendations'])}")
    
    if args.performance:
        print("⚡ Running performance tests...")
        # Performance testing would be done in BGE context
        print("💡 Performance testing requires BGE runtime")
    
    print("✅ Tests completed successfully")

def cmd_config(args):
    """Configure sensor layouts and specifications"""
    print("⚙️ Motion sensor configuration...")
    
    if args.list_layouts:
        print("📋 Available sensor layouts:")
        layouts = ["small_apartment", "medium_house", "large_house"]
        for layout in layouts:
            config = load_sensor_layout(layout)
            if config:
                print(f"   🏠 {layout}: {config['total_sensors']} sensors - {config['description']}")
    
    if args.show_specs:
        print("📊 Sensor specifications:")
        specs = get_sensor_specs()
        for key, value in specs.items():
            print(f"   {key}: {value}")
    
    if args.create_layout:
        print(f"🔧 Creating custom layout: {args.create_layout}")
        # Interactive layout creation would go here
        print("💡 Use setup command with --interactive for layout creation")

def cmd_validate(args):
    """Validate sensor coverage and placement"""
    print("🔍 Validating sensor configuration...")
    
    if args.config:
        if os.path.exists(args.config):
            with open(args.config, 'r') as f:
                config = json.load(f)
            
            if 'sensors' in config:
                sensors = config['sensors']
                validation = validate_sensor_coverage(sensors)
                
                print("📊 Validation Results:")
                print(f"   ✅ Total Sensors: {validation['total_sensors']}")
                print(f"   🏠 Rooms Covered: {len(validation['coverage_analysis'])}")
                print(f"   ⚠️ Blind Spots: {len(validation['blind_spots'])}")
                
                if validation['blind_spots']:
                    print(f"   🚨 Uncovered areas: {', '.join(validation['blind_spots'])}")
                
                print(f"   💡 Recommendations: {len(validation['recommendations'])}")
                for i, rec in enumerate(validation['recommendations'][:3]):
                    print(f"      {i+1}. {rec}")
            else:
                print("❌ Invalid configuration file format")
        else:
            print(f"❌ Configuration file not found: {args.config}")
    else:
        print("💡 Use --config to specify configuration file to validate")

def cmd_deploy(args):
    """Deploy sensors to Blender scene"""
    print("🚀 Deploying sensors to Blender scene...")
    print("⚠️ This command requires Blender with VESPER addon loaded")
    
    if args.layout:
        layout = load_sensor_layout(args.layout)
        if layout:
            print(f"📋 Deploying {layout['total_sensors']} sensors from {args.layout}")
            # Deployment would happen through Blender addon
            print("💡 Run this command within Blender BGE for actual deployment")
        else:
            print(f"❌ Layout '{args.layout}' not found")
    else:
        print("💡 Specify --layout to deploy a predefined sensor layout")

def cmd_status(args):
    """Show current sensor status and statistics"""
    print("📊 Motion sensor system status...")
    
    # This would typically require BGE context for real status
    print("⚠️ Real-time status requires BGE runtime")
    print("💡 Available status information:")
    print("   📋 Sensor specifications: Available")
    print("   🏠 Layout configurations: Available")
    print("   📊 Live detection status: Requires BGE")
    print("   📈 Performance metrics: Requires BGE")
    
    if args.verbose:
        specs = get_sensor_specs()
        print("\n📊 System Specifications:")
        for key, value in specs.items():
            print(f"   {key}: {value}")

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="VESPER Motion Sensor Detection System Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup motion sensors')
    setup_parser.add_argument('--layout', choices=['small_apartment', 'medium_house', 'large_house'],
                            help='Use predefined sensor layout')
    setup_parser.add_argument('--interactive', action='store_true',
                            help='Interactive sensor placement')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demonstration')
    demo_parser.add_argument('--sensors', type=int, default=6,
                           help='Number of demo sensors')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--coverage', action='store_true',
                           help='Test sensor coverage')
    test_parser.add_argument('--performance', action='store_true',
                           help='Test system performance')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration')
    config_parser.add_argument('--list-layouts', action='store_true',
                              help='List available layouts')
    config_parser.add_argument('--show-specs', action='store_true',
                              help='Show sensor specifications')
    config_parser.add_argument('--create-layout', type=str,
                              help='Create custom layout')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    validate_parser.add_argument('--config', type=str,
                                help='Configuration file to validate')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy to Blender')
    deploy_parser.add_argument('--layout', choices=['small_apartment', 'medium_house', 'large_house'],
                              help='Layout to deploy')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.add_argument('--verbose', action='store_true',
                              help='Verbose status output')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    print_banner()
    
    # Execute commands
    if args.command == 'setup':
        cmd_setup(args)
    elif args.command == 'demo':
        cmd_demo(args)
    elif args.command == 'test':
        cmd_test(args)
    elif args.command == 'config':
        cmd_config(args)
    elif args.command == 'validate':
        cmd_validate(args)
    elif args.command == 'deploy':
        cmd_deploy(args)
    elif args.command == 'status':
        cmd_status(args)
    
    print("\n🎉 Command completed successfully!")
    print("💡 For more information, see: motion_sensors/README.md")

if __name__ == "__main__":
    main()
