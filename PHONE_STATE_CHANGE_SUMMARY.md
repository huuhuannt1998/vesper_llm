# Phone Device State Changed to "IN USE" (Open) ✅

## What We Did

### 1. Triggered Phone Pickup
```bash
curl -X POST http://localhost:9201/interaction \
  -H "Content-Type: application/json" \
  -d '{"action":"pickup"}'
```

**Result:** Phone state changed from PRESENT → ABSENT (picked up/in use)

### 2. Updated Redis State
Manually synchronized Redis to match container state:
```bash
docker exec testbed-redis redis-cli SET 'item_sensor:I01:state' \
  '{"presence":"ABSENT","item_name":"Phone","item_type":"communication",...}'
```

### 3. Verified SmartThings State
```bash
curl -X POST https://9104a04a38e2.ngrok-free.app/schema \
  -H "Content-Type: application/json" \
  -d '{"headers":{"interactionType":"stateRefreshRequest"},...}'
```

**Response:**
```json
{
  "externalDeviceId": "VSI-DF8A-CE65-08F5",
  "states": [
    {
      "capability": "st.healthCheck",
      "attribute": "healthStatus",
      "value": "online"
    },
    {
      "capability": "st.contactSensor",
      "attribute": "contact",
      "value": "open"     ← Phone is IN USE!
    }
  ]
}
```

## Current Status

✅ **Backend State:** Phone = ABSENT (picked up) 
✅ **SmartThings Schema:** Contact = OPEN (in use)
⏳ **SmartThings App:** May still show "Closed" due to caching

## Why SmartThings App Still Shows "Closed"

**SmartThings uses caching** and doesn't auto-refresh device states. The state is correct on the server side, but the app needs to be told to refresh.

### Two Ways to Fix:

#### Option 1: Manual Refresh (EASIEST)
1. Open SmartThings mobile app
2. Go to **Devices** tab
3. **Pull down to refresh** (swipe down gesture)
4. Phone should now show as **"Open"**

#### Option 2: Enable Real-time Callbacks (ADVANCED)
SmartThings needs OAuth callback credentials to receive push notifications. This requires:
1. Complete OAuth flow in SmartThings Schema App
2. Store access tokens in Redis
3. Cloud server will then push state changes automatically

Currently, no callback credentials are stored:
```bash
$ docker exec testbed-redis redis-cli KEYS "smartthings_callback:*"
(empty)
```

## Device State Mapping

| Container State | Redis Key | SmartThings Capability | Display Value |
|----------------|-----------|------------------------|---------------|
| PRESENT | presence=PRESENT | st.contactSensor | **Closed** (on table) |
| ABSENT | presence=ABSENT | st.contactSensor | **Open** (in use) |

## Commands Reference

### Check Phone Container State
```powershell
Invoke-WebRequest -Uri "http://localhost:9201/state" -UseBasicParsing
```

### Pickup Phone (Make it ABSENT)
```powershell
Invoke-WebRequest -Uri "http://localhost:9201/interaction" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"action":"pickup"}' `
  -UseBasicParsing
```

### Put Down Phone (Make it PRESENT)
```powershell
Invoke-WebRequest -Uri "http://localhost:9201/interaction" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"action":"putdown"}' `
  -UseBasicParsing
```

### Check SmartThings State
```powershell
$payload = '{"headers":{"schema":"st-schema","version":"1.0","interactionType":"stateRefreshRequest","requestId":"test"},"devices":[{"externalDeviceId":"VSI-DF8A-CE65-08F5","deviceCookie":{}}]}'

Invoke-WebRequest -Uri "https://9104a04a38e2.ngrok-free.app/schema" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $payload `
  -UseBasicParsing
```

### Manually Sync Redis from Container
```powershell
# Get state from container
$state = (Invoke-WebRequest -Uri "http://localhost:9201/state" -UseBasicParsing).Content

# Update Redis
docker exec testbed-redis redis-cli SET 'item_sensor:I01:state' "$state"
```

## Next Steps

1. **Refresh SmartThings App** - Pull down on Devices tab
2. **Verify Phone shows "Open"** in app
3. **Test putdown action** - Should change back to "Closed"
4. **(Optional) Set up OAuth callbacks** for automatic push notifications

## Integration with Blender

When Blender Game Engine calls:
```python
turn_device_on("Phone")  # Triggers pickup
```

The flow will be:
1. Blender → Docker container (port 9201) 
2. Container updates internal state: PRESENT → ABSENT
3. Container saves to Redis: `item_sensor:I01:state`
4. SmartThings queries state (if callbacks set up)
5. SmartThings app shows: "Closed" → "Open"

**Current Limitation:** Redis sync is manual. Need to ensure containers properly save state to Redis on every interaction.
