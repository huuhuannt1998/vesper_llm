# SmartThings Cloud-to-Cloud Integration Setup Guide

This guide provides detailed step-by-step instructions for setting up the Virtual Thermostat Testbed with SmartThings cloud-to-cloud integration using SmartThings Schema.

## Prerequisites

Before starting, ensure you have:
- Docker and Docker Compose installed
- A SmartThings Developer account
- An ngrok account (free tier is sufficient)
- Basic understanding of OAuth 2.0
- A smartphone with the SmartThings app installed

## Architecture Overview

The integration consists of:
1. **OAuth 2.0 Authorization Server** - Handles authentication between SmartThings and your cloud
2. **Schema App** - Processes SmartThings Schema interactions
3. **Device Management** - Virtual thermostats and environment simulators

## Step 1: Start the Virtual Thermostat Testbed

### 1.1 Clone and Navigate to the Project
```bash
cd virtual-thermostat-testbed
```

### 1.2 Configure Environment Variables
Create a `.env` file with your credentials:
```env
# SmartThings Configuration (working tested credentials)
SMARTTHINGS_CLIENT_ID=virtual-thermostat-testbed-2025-v1
SMARTTHINGS_CLIENT_SECRET=VT_Secret_2025_NgKx7mP9QwE3RtY8UiO5pLsA6bF4cH2jD9vK8xM1nR6tG3zC7wE4

# Ngrok Configuration (with reserved static domain)
NGROK_AUTH_TOKEN=2eEdMNa3XkIOw7CsHuV7crgAtbD_6hdTjRRUawk5bA2PTdWX5
NGROK_DOMAIN=vt-testbed-2025.ngrok.app

# Security
JWT_SECRET=VT_JWT_Secret_2025_Production_Ready_Key_Change_In_Production
```

### 1.3 Start the Services
```bash
chmod +x scripts/start-testbed.sh
./scripts/start-testbed.sh
```

Note: If you encounter errors with the old startup.sh script, use the new start-testbed.sh which has better error handling and Docker Compose v2 support.

### 1.4 Verify Services are Running
```bash
docker-compose ps
```

You should see:
- testbed-redis
- testbed-postgres
- testbed-cloud-server
- testbed-ngrok (new dedicated ngrok container)
- testbed-backend-console

### 1.5 Verify Static Domain Access
With the new architecture, your static domain is pre-configured. Test access:
```bash
curl https://vt-testbed-2025.ngrok.app/health
```

You should see:
```json
{"status":"healthy","webhook_url":null}
```

**Your Static Domain**: `https://vt-testbed-2025.ngrok.app` - this URL is consistent and won't change!

**Important**: This static domain is now ready for SmartThings configuration.

## Step 2: Configure OAuth 2.0 Server

Our testbed includes a built-in OAuth 2.0 server that supports:
- Authorization code flow
- Multiple redirect URIs
- Token refresh

### 2.1 Verify OAuth Endpoints

Your OAuth endpoints are:
- **Authorization URL**: `https://vt-testbed-2025.ngrok.app/oauth/authorize`
- **Token URL**: `https://vt-testbed-2025.ngrok.app/oauth/token`

### 2.2 Supported Redirect URIs

The server automatically supports all required SmartThings redirect URIs:
- `https://c2c-us.smartthings.com/oauth/callback` (United States)
- `https://c2c-eu.smartthings.com/oauth/callback` (European Union)
- `https://c2c-ap.smartthings.com/oauth/callback` (Asia-Pacific)

## Step 3: Create SmartThings Developer Account

### 3.1 Sign Up for Developer Account
1. Go to https://smartthings.developer.samsung.com/
2. Click "Sign In" and create a Samsung account if you don't have one
3. Complete the developer registration

### 3.2 Access Developer Center
1. Log in to the Developer Center
2. Navigate to "Projects" section

## Step 4: Create a New Project

### 4.1 Create Project
1. Click "New Project"
2. Enter project details:
   - **Project Name**: Virtual Thermostat Testbed
   - **Description**: Virtual thermostats for energy research
   - **Project Type**: Device Integration
3. Click "Create Project"

## Step 5: Register Cloud Connector

### 5.1 Add Cloud Connector
1. In your project, click "Add" → "Device Integration" → "Cloud Connector"
2. Select "SmartThings Schema" as the connector type

### 5.2 Configure Connector Details

Fill in the following information:

**Basic Information:**
- **Connector Name**: Virtual Thermostat Cloud Connector
- **Description**: Connects virtual thermostats to SmartThings
- **Category**: Climate Control

**Schema Configuration:**
- **Schema Connector Type**: HTTPS
- **Schema Endpoint URL**: `https://vt-testbed-2025.ngrok.app/schema`
- **Host Type**: Static (using reserved domain)

**OAuth Configuration:**
- **Client ID**: `virtual-thermostat-testbed-2025-v1` (pre-configured)
- **Client Secret**: `VT_Secret_2025_NgKx7mP9QwE3RtY8UiO5pLsA6bF4cH2jD9vK8xM1nR6tG3zC7wE4` (pre-configured)
- **Authorization URI**: `https://vt-testbed-2025.ngrok.app/oauth/authorize`
- **Token URI**: `https://vt-testbed-2025.ngrok.app/oauth/token`
- **Scopes**: Enter `device:all`

**Note**: The credentials are already configured in your `.env` file - just use these exact values!

### 5.3 Configure Device Profile

Add supported capabilities:
1. Click "Add Capability"
2. Add the following capabilities:
   - `temperatureMeasurement`
   - `thermostat`
   - `thermostatMode`
   - `thermostatCoolingSetpoint`
   - `thermostatHeatingSetpoint`
   - `thermostatFanMode`
   - `thermostatOperatingState`
   - `relativeHumidityMeasurement`

### 5.4 Save and Deploy
1. Click "Save"
2. Click "Deploy to Test"

## Step 6: Test the Integration

### 6.1 Enable Developer Mode in SmartThings App
1. Open the SmartThings app on your phone
2. Go to Menu → Settings
3. Tap on "About SmartThings" 5 times to enable Developer Mode
4. Enable "Developer Mode" toggle

### 6.2 Add Your Cloud Connector
1. In SmartThings app, tap "+" → "Device"
2. Tap "By brand"
3. Search for "My Testing Devices"
4. Select your "Virtual Thermostat Cloud Connector"

### 6.3 Complete OAuth Flow
1. You'll be redirected to your OAuth login page
2. Default credentials:
   - Username: `admin`
   - Password: `admin123`
3. Click "Authorize" to grant access

### 6.4 Discover Devices
1. SmartThings will send a discovery request
2. The testbed will respond with available virtual thermostats
3. Select the devices you want to add

## Step 7: Spawn Virtual Devices

### 7.1 Access Backend Console
Open http://localhost:3000 in your browser

### 7.2 Create Virtual Thermostats
Use the API to spawn devices:
```bash
curl -X POST http://localhost:8088/api/console/spawn \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "environment_config": "medium_house_efficient.yaml"
  }'
```

### 7.3 Verify in SmartThings
1. Pull down to refresh in the SmartThings app
2. Your new virtual thermostat should appear

## Step 8: Test Device Control

### 8.1 Control from SmartThings App
1. Tap on a virtual thermostat
2. Try changing:
   - Temperature setpoint
   - Thermostat mode (heat/cool/auto/off)
   - Fan mode (auto/on)

### 8.2 Monitor State Changes
Watch the logs to see commands being processed:
```bash
docker-compose logs -f cloud-server thermostat-*
```

### 8.3 Check Power Consumption
Access HELICs API to see power data:
```bash
curl http://localhost:8088/api/helics/power-consumption
```

## Step 9: Production Deployment

For production deployment:

### 10.1 Replace Ngrok
- Set up a proper domain with SSL certificate
- Use a reverse proxy (nginx/Apache)
- Update SmartThings connector with production URL

### 10.2 Security Hardening
- Change default passwords
- Use strong JWT secret
- Implement rate limiting
- Enable HTTPS only

### 10.3 Scaling
- Use Kubernetes for container orchestration
- Implement Redis clustering
- Add load balancing

## Troubleshooting

### Common Issues and Solutions

#### 1. OAuth Authorization Fails
- **Issue**: "Invalid client" error
- **Solution**: Verify SMARTTHINGS_CLIENT_ID and SMARTTHINGS_CLIENT_SECRET match exactly

#### 2. Devices Not Discovered
- **Issue**: No devices appear in SmartThings
- **Solution**: 
  - Check cloud-server logs for discovery requests
  - Ensure devices are spawned and have state in Redis
  - Verify Schema endpoint is accessible

#### 3. Commands Not Working
- **Issue**: Commands from SmartThings don't affect devices
- **Solution**:
  - Check thermostat container logs
  - Verify Redis connectivity
  - Ensure command queue is being processed

#### 4. Ngrok Connection Issues
- **Issue**: Ngrok tunnel not establishing
- **Solution**:
  - Verify NGROK_AUTH_TOKEN is correct
  - Check ngrok service status
  - Try restarting cloud-server container

### Debug Commands

Check Schema endpoint:
```bash
curl -X POST https://vt-testbed-2025.ngrok.app/schema \
  -H "Content-Type: application/json" \
  -d '{
    "headers": {
      "schema": "st-schema",
      "version": "1.0",
      "interactionType": "discoveryRequest",
      "requestId": "test-123"
    }
  }'
```

Monitor Redis:
```bash
docker exec testbed-redis redis-cli MONITOR
```

Check container health:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## Schema Interaction Types Reference

Your Schema App handles these interaction types:

### discoveryRequest
Returns list of available devices

### stateRefreshRequest
Returns current state of specified devices

### commandRequest
Processes commands and returns updated state

### grantCallbackAccess
Stores callback URLs for proactive state updates

### integrationDeleted
Cleanup when integration is removed

## Next Steps

1. **Scale Testing**: Use the batch spawn script to create 100+ devices
2. **Weather Simulation**: Override outside temperature for all devices
3. **Energy Analysis**: Use HELICs API for power grid simulation
4. **Custom Automations**: Create SmartThings routines with your devices

## Support Resources

- SmartThings Developer Forum: https://community.smartthings.com/
- SmartThings API Reference: https://developer.smartthings.com/docs/api/public
- Project Issues: Create an issue on GitHub
- Logs: Always check `docker-compose logs` for debugging

## Security Best Practices

1. **Never commit credentials** to version control
2. **Rotate secrets** regularly
3. **Use HTTPS** for all production endpoints
4. **Implement rate limiting** on APIs
5. **Monitor for suspicious activity**

Remember: This testbed is for research and development. For production use, implement additional security measures and follow SmartThings certification requirements.
