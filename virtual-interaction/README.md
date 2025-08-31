# Virtual Smart Thermostat Testbed

A scalable testbed simulating 1000+ smart home thermostats for energy consumption research. This system provides virtual thermostat devices integrated with SmartThings through cloud-to-cloud connection, complete with realistic thermal dynamics simulation and HELICs integration for power grid studies.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SmartThings Cloud                             │
│                  (Cloud-to-Cloud Integration)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  ngrok  │
                    │ tunnel  │
                    └────┬────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      Cloud Server                                │
│     (SmartThings Integration, OAuth, User Management)            │
└────────────────────────┬────────────────────────────────────────┘
                         │ Docker Network (172.22.0.0/16)
┌────────────────────────┼────────────────────────────────────────┐
│   ┌─────────────┐      │      ┌─────────────┐                   │
│   │ Thermostat  │◄─────┼─────►│Environment  │                   │
│   │ Container 1 │      │      │ Simulator 1 │                   │
│   └─────────────┘      │      └─────────────┘                   │
│         ...            │            ...                          │
│   ┌─────────────┐      │      ┌─────────────┐                   │
│   │ Thermostat  │◄─────┼─────►│Environment  │                   │
│   │Container 1000│     │      │Simulator 1000│                  │
│   └─────────────┘      │      └─────────────┘                   │
└────────────────────────┼────────────────────────────────────────┘
                         │
                    ┌────▼────┐         ┌─────────┐
                    │  Redis  │         │Backend  │
                    │Database │◄────────┤Control  │ ──► HELICs
                    └─────────┘         │Console  │     Simulator
                                       └─────────┘
```

## Features

- **Scalable Architecture**: Supports 1000+ virtual thermostat devices
- **SmartThings Integration**: Full cloud-to-cloud integration with OAuth
- **Realistic Simulation**: Thermal dynamics modeling with configurable home profiles
- **HELICs Integration**: Real-time power consumption data for grid simulation
- **Container Management**: Dynamic spawning of device pairs via Docker
- **Web Console**: Management interface for monitoring and control
- **Data Export**: Comprehensive data export for research analysis

## Components

### 1. Virtual Thermostat Container
- Simulates smart thermostat behavior on port 8000
- Implements standard thermostat capabilities
- Communicates with cloud server and environment simulator
- Maintains state in Redis

### 2. Environment Simulator Container
- Models thermal dynamics of different home types on port 8001
- Simulates outside temperature variations
- Calculates energy consumption based on HVAC operation
- Configurable via YAML profiles

### 3. Cloud Server (Port 8080)
- Handles SmartThings cloud-to-cloud integration
- Manages OAuth authentication flow
- Provides ngrok tunnel for webhook access
- PostgreSQL database for user/device management

### 4. Backend Control Console (Port 8088)
- RESTful API for system management
- HELICs integration endpoints
- Container orchestration via Docker API
- WebSocket support for real-time updates
- Weather override capabilities

### 5. Frontend Console (Port 3000)
- React-based web interface
- Device management and monitoring
- Real-time power consumption visualization

## Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM for running multiple containers
- Linux/macOS (Windows WSL2 supported)
- ngrok account (free tier sufficient)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/virtual-thermostat-testbed.git
cd virtual-thermostat-testbed
```

2. **Configure environment variables**
Create a `.env` file with your credentials:
```env
# SmartThings Configuration
SMARTTHINGS_CLIENT_ID=virtual-thermostat-testbed-2025-v1
SMARTTHINGS_CLIENT_SECRET=VT_Secret_2025_NgKx7mP9QwE3RtY8UiO5pLsA6bF4cH2jD9vK8xM1nR6tG3zC7wE4

# Ngrok Configuration
NGROK_AUTH_TOKEN=2eEdMNa3XkIOw7CsHuV7crgAtbD_6hdTjRRUawk5bA2PTdWX5
NGROK_DOMAIN=vt-testbed-2025.ngrok.app

# Security
JWT_SECRET=VT_JWT_Secret_2025_Production_Ready_Key_Change_In_Production
```

3. **Make startup script executable**
```bash
chmod +x scripts/start-testbed.sh
```

4. **Run the startup script**
```bash
./scripts/start-testbed.sh
```

5. **Access the console**
- Web Console: http://localhost:3000
- Backend API: http://localhost:8088
- HELICs API: http://localhost:8088/api/helics
- Cloud Server: http://localhost:8080

## Configuration

### Environment Profiles

The testbed includes predefined home configurations in `/config/environments/`:

- `small_apartment_efficient.yaml` - 800 sqft, high efficiency
- `small_apartment_inefficient.yaml` - 800 sqft, poor efficiency
- `medium_house_efficient.yaml` - 2000 sqft, high efficiency

*Note: Additional configurations can be created by copying and modifying existing YAML files.*

### SmartThings Integration Setup

#### Step 1: Create SmartThings Developer Account
1. Go to https://smartthings.developer.samsung.com/
2. Create an account and workspace

#### Step 2: Create Schema Cloud Connector
1. Navigate to "Cloud Connectors" → "Schema Connectors"
2. Click "New Schema Connector"
3. Configure the following:
   - **Connector Name**: Virtual Thermostat Testbed
   - **Schema Endpoint URL**: `https://vt-testbed-2025.ngrok.app/schema`
   - **Client ID**: `virtual-thermostat-testbed-2025-v1`
   - **Client Secret**: `VT_Secret_2025_NgKx7mP9QwE3RtY8UiO5pLsA6bF4cH2jD9vK8xM1nR6tG3zC7wE4`

#### Step 3: Configure OAuth Settings
- **Authorization URI**: `https://vt-testbed-2025.ngrok.app/oauth/authorize`
- **Token URI**: `https://vt-testbed-2025.ngrok.app/oauth/token`
- **Scopes**: `device:all`

#### Step 4: Configure Device Profile
Add the following capabilities:
- `temperatureMeasurement`
- `thermostat`
- `thermostatMode`
- `thermostatCoolingSetpoint`
- `thermostatHeatingSetpoint`
- `thermostatFanMode`
- `thermostatOperatingState`
- `relativeHumidityMeasurement`

#### Step 5: Deploy and Test
1. Save and deploy the connector
2. Enable developer mode in SmartThings app
3. Add your cloud connector
4. Complete OAuth flow (default: admin/admin123)

## API Documentation

### Device Management

**Spawn New Device Pair**
```bash
POST /api/console/spawn
{
  "username": "research_user",
  "environment_config": "medium_house_efficient.yaml"
}
```

**List All Devices**
```bash
GET /api/console/devices
```

**Delete Device**
```bash
DELETE /api/console/device/{serial}
```

### Weather Control

**Override Temperature (All Devices)**
```bash
POST /api/console/weather-override
{
  "temperature": 95.0,
  "duration_hours": 4
}
```

**Override Temperature (Single Device)**
```bash
POST /api/console/device/{serial}/weather-override
{
  "temperature": 30.0
}
```

### Device Control

**Set Temperature**
```bash
POST /api/console/device/{serial}/setpoint
{
  "target_temp": 72.0
}
```

**Set Mode**
```bash
POST /api/console/device/{serial}/mode
{
  "mode": "cool"
}
```

### HELICs Integration

**Get All Power Consumption**
```bash
GET /api/helics/power-consumption
```

Response:
```json
{
  "timestamp": "2024-01-20T10:00:00Z",
  "total_homes": 1000,
  "total_power_kw": 3500.5,
  "homes": [
    {
      "home_id": "VST-1234-5678-9012",
      "power_kw": 3.5,
      "hvac_state": "cooling",
      "indoor_temp": 72.0,
      "outdoor_temp": 95.0,
      "setpoint": 72.0,
      "efficiency_rating": 16.0,
      "home_size_sqft": 2000
    }
  ]
}
```

**WebSocket Stream**
```javascript
const ws = new WebSocket('ws://localhost:8088/api/helics/stream');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle power updates
};
```

**Get Single Device Power**
```bash
GET /api/helics/power-consumption/{serial}
```

### Data Export

**Export User Data**
```bash
GET /api/console/export/{username}
```

## Service Reference

### Cloud Server (Port 8080)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check and ngrok URL |
| POST | `/api/devices/register` | Register device with system |
| GET | `/api/devices` | List all registered devices |
| POST | `/api/devices/{device_id}/state` | Update device state |
| POST | `/schema` | SmartThings Schema endpoint |
| GET | `/oauth/authorize` | OAuth authorization endpoint |
| POST | `/oauth/token` | OAuth token endpoint |

### Backend Console (Port 8088)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| POST | `/api/console/spawn` | Spawn new device pair |
| GET | `/api/console/devices` | List devices with status |
| DELETE | `/api/console/device/{serial}` | Remove device |
| GET | `/api/console/dashboard` | System dashboard data |
| POST | `/api/console/weather-override` | Global weather control |
| GET | `/api/helics/power-consumption` | Power data for HELICs |
| WS | `/api/helics/stream` | Real-time power stream |

### Thermostat Device (Port 8000)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Device health and serial |
| GET | `/api/v1/device/status` | Current device state |
| POST | `/api/v1/device/setpoint` | Change temperature setpoint |
| POST | `/api/v1/device/mode` | Change HVAC mode |
| POST | `/api/v1/device/fan` | Change fan mode |

### Environment Simulator (Port 8001)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Simulator health |
| GET | `/api/v1/status` | Current environmental data |
| POST | `/api/v1/override/temperature` | Override outside temperature |
| GET | `/api/v1/power` | Power consumption data |

## Scaling to 1000 Devices

### Recommended Approach

1. **Start Small**: Begin with 10-50 devices to verify functionality
2. **Batch Spawning**: Use scripts to spawn devices in batches
3. **Monitor Resources**: Watch CPU, memory, and network usage
4. **Optimize Redis**: Configure Redis persistence and memory limits
5. **Load Balance**: Consider multiple Docker hosts for large deployments

### Example Batch Spawn Script

```python
import requests
import time
import random

configs = [
    "small_apartment_efficient.yaml",
    "medium_house_efficient.yaml",
    "small_apartment_inefficient.yaml"
]

for i in range(1000):
    config = random.choice(configs)
    response = requests.post(
        "http://localhost:8088/api/console/spawn",
        json={
            "username": f"user_{i//100}",
            "environment_config": config
        }
    )
    if i % 10 == 0:
        print(f"Spawned {i} devices...")
    time.sleep(0.5)  # Avoid overwhelming the system
```

## Redis Key-space Convention

| Pattern | Contents |
|---------|----------|
| `thermostat:{serial}:state` | Current device state JSON |
| `thermostat:{serial}:history` | Historical state entries |
| `thermostat:{serial}:commands` | Pending command queue |
| `thermostat:{serial}:hvac_state` | HVAC operation flag |
| `environment:{serial}:state` | Environmental parameters |
| `environment:{serial}:power` | Power consumption data |
| `device:{serial}:metadata` | Device spawn metadata |
| `smartthings_callback:{user_id}` | OAuth callback tokens |

## Database Schema

```sql
-- Users table
users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE,
  password_hash TEXT,
  created_at TIMESTAMP
);

-- Devices table  
devices (
  id INTEGER PRIMARY KEY,
  serial_number TEXT UNIQUE,
  device_id TEXT UNIQUE,
  user_id INTEGER REFERENCES users(id),
  smartthings_device_id TEXT,
  created_at TIMESTAMP,
  config_file TEXT
);

-- OAuth tokens
oauth_tokens (
  id INTEGER PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  access_token TEXT UNIQUE,
  refresh_token TEXT UNIQUE,
  expires_at TIMESTAMP,
  created_at TIMESTAMP
);
```

## Environment Variables

| Variable | Default | Used by |
|----------|---------|---------|
| `DATABASE_URL` | postgresql://... | cloud-server, console-backend |
| `REDIS_URL` | redis://redis:6379 | cloud-server, console-backend |
| `CLOUD_SERVER_URL` | http://cloud-server:8080 | console-backend, thermostat |
| `NGROK_AUTH_TOKEN` | - | ngrok container |
| `NGROK_DOMAIN` | - | ngrok container |
| `JWT_SECRET` | - | cloud-server |
| `SMARTTHINGS_CLIENT_ID` | - | cloud-server OAuth |
| `SMARTTHINGS_CLIENT_SECRET` | - | cloud-server OAuth |
| `REACT_APP_API_URL` | http://localhost:8088 | console-frontend |

## Monitoring

### Container Health
```bash
docker-compose ps
docker stats
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f cloud-server
docker-compose logs -f thermostat-*
```

### Redis Monitoring
```bash
docker exec testbed-redis redis-cli INFO
```

## Troubleshooting

### Common Issues

1. **Container Spawn Failures**
   - Check Docker daemon socket permissions
   - Verify image names in spawn function
   - Check available system resources

2. **Network Communication Issues**
   - Ensure all containers are on testbed-network (172.22.0.0/16)
   - Check container name resolution
   - Verify port bindings

3. **High Memory Usage**
   - Limit Redis memory: `maxmemory 2gb`
   - Reduce history retention
   - Implement data archival

4. **SmartThings Integration Issues**
   - Verify ngrok tunnel is active
   - Check OAuth credentials match exactly
   - Ensure Schema endpoint is accessible
   - Monitor cloud-server logs for discovery/command requests

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

Monitor Redis activity:
```bash
docker exec testbed-redis redis-cli MONITOR
```

Test OAuth flow:
```bash
curl https://vt-testbed-2025.ngrok.app/oauth/authorize
```

## Performance Optimization

### Redis Optimization
- Use Redis persistence wisely
- Configure appropriate eviction policies
- Consider Redis Cluster for very large deployments

### Container Optimization
- Use Alpine-based images
- Limit container resources
- Implement health checks

### Network Optimization
- Use container names for internal communication
- Minimize cross-container API calls
- Batch updates when possible

## Security Considerations

1. **Change Default Passwords**: Update admin password and JWT secret
2. **Network Isolation**: Use Docker networks appropriately (testbed-network)
3. **API Authentication**: Implement proper authentication for production
4. **Data Encryption**: Use TLS for external communications
5. **Access Control**: Limit Docker socket access
6. **Credential Management**: Never commit secrets to version control

## Production Deployment

### Replace Ngrok
- Set up proper domain with SSL certificate
- Use reverse proxy (nginx/Apache)
- Update SmartThings connector with production URL

### Security Hardening
- Change default passwords
- Use strong JWT secret
- Implement rate limiting
- Enable HTTPS only

### Scaling
- Use Kubernetes for container orchestration
- Implement Redis clustering
- Add load balancing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting guide
- Review container logs for detailed error messages

## Roadmap

- [ ] Kubernetes deployment support
- [ ] Advanced scheduling algorithms
- [ ] Machine learning integration
- [ ] Enhanced visualization dashboard
- [ ] Multi-region simulation support
- [ ] Integration with real weather APIs
- [ ] Additional home profile configurations
- [ ] Advanced power modeling algorithms