import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Container, 
  Typography, 
  Button, 
  Box, 
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Stack,
  Tabs,
  Tab
} from '@mui/material';
import { 
  Thermostat, 
  Cloud, 
  Power, 
  Delete, 
  Refresh, 
  PlayArrow,
  Stop,
  Settings,
  TrendingUp,
  WbSunny,
  AcUnit,
  DeviceThermostat,
  People
} from '@mui/icons-material';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8088';
const CLOUD_URL = process.env.REACT_APP_CLOUD_URL || 'http://localhost:8081';

function App() {
  /* ------------------ Common State ------------------ */
  const [tabIndex, setTabIndex] = useState(0);          // 0 = Devices, 1 = Users
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  /* ------------------ Device State ------------------ */
  const [devices, setDevices] = useState([]);
  const [usernameInput, setUsernameInput] = useState('admin');
  const [powerData, setPowerData] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, device: null });
  const [controlDialog, setControlDialog] = useState({ open: false, device: null });
  const [setpointDialog, setSetpointDialog] = useState({ open: false, device: null, value: 72 });
  const [modeDialog, setModeDialog] = useState({ open: false, device: null, value: 'auto' });
  const [weatherDialog, setWeatherDialog] = useState({ open: false, device: null, value: 85 });
  const [currentTempDialog, setCurrentTempDialog] = useState({ open: false, device: null, value: 72 });

  /* ------------------ User Management State ------------------ */
  const [users, setUsers] = useState([]);
  const [userLoading, setUserLoading] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');

  /* ------------------ Effects ------------------ */
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  /* ------------------ Data Loaders ------------------ */
  const loadData = async () => {
    setRefreshing(true);
    try {
      await Promise.all([
        fetchDevices(),
        fetchPowerData(),
        fetchDashboardData(),
        fetchUsers()
      ]);
    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/console/devices`);
      setDevices(response.data || []);
    } catch (err) {
      console.error('Error fetching devices:', err);
      setDevices([]);
    }
  };

  const fetchPowerData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/helics/power-consumption`);
      setPowerData(response.data);
    } catch (err) {
      console.error('Error fetching power data:', err);
      setPowerData(null);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/console/dashboard`);
      setDashboardData(response.data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setDashboardData(null);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${CLOUD_URL}/api/users`);
      setUsers(response.data || []);
    } catch (err) {
      console.error('Error fetching users:', err);
      setUsers([]);
    }
  };

  /* ------------------ User CRUD ------------------ */
  const createUser = async () => {
    if (!newUsername || !newPassword) {
      setError('Username and password required');
      return;
    }
    setUserLoading(true);
    try {
      await axios.post(`${CLOUD_URL}/api/users/register`, null, {
        params: { username: newUsername, password: newPassword }
      });
      setSuccess(`User "${newUsername}" created`);
      setNewUsername('');
      setNewPassword('');
      await fetchUsers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setUserLoading(false);
    }
  };

  /* ------------------ Device Operations ------------------ */
  const spawnDevice = async (config) => {
    if (!usernameInput.trim()) {
      setError('Username is required');
      return;
    }
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.post(`${API_URL}/api/console/spawn`, {
        username: usernameInput.trim(),
        environment_config: config
      });

      const serial = response.data.serial_number;

      /* -------------------------------------------------------------
       * ALSO register the new thermostat with the cloud-server so it
       * can be discovered by SmartThings.
       * -----------------------------------------------------------*/
      // await axios.post(`${CLOUD_URL}/api/devices/register`, {
      //   serial_number: serial,
      //   device_type: 'thermostat',
      //   capabilities: [
      //     'temperatureMeasurement',
      //     'thermostatCoolingSetpoint',
      //     'thermostatHeatingSetpoint',
      //     'thermostatMode',
      //     'thermostatFanMode'
      //   ],
      //   username: usernameInput.trim()
      // });

      setSuccess(`Successfully created & registered device: ${serial}`);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to spawn device');
    } finally {
      setLoading(false);
    }
  };

  const deleteDevice = async (serial) => {
    try {
      await axios.delete(`${API_URL}/api/console/device/${serial}`);
      setSuccess(`Successfully deleted device: ${serial}`);
      setDeleteDialog({ open: false, device: null });
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete device');
    }
  };

  const updateSetpoint = async (serial, temperature) => {
    try {
      await axios.post(`${API_URL}/api/console/device/${serial}/setpoint`, {
        target_temp: temperature
      });
      setSuccess(`Updated setpoint for ${serial} to ${temperature}°F`);
      setSetpointDialog({ open: false, device: null, value: 72 });
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update setpoint');
    }
  };

  const updateMode = async (serial, mode) => {
    try {
      await axios.post(`${API_URL}/api/console/device/${serial}/mode`, {
        mode: mode
      });
      setSuccess(`Updated mode for ${serial} to ${mode}`);
      setModeDialog({ open: false, device: null, value: 'auto' });
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update mode');
    }
  };

  const overrideWeather = async (serial, temperature) => {
    try {
      await axios.post(`${API_URL}/api/console/device/${serial}/weather-override`, {
        temperature: temperature
      });
      setSuccess(`Set outdoor temperature for ${serial} to ${temperature}°F`);
      setWeatherDialog({ open: false, device: null, value: 85 });
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to override weather');
    }
  };

  const updateCurrentTemp = async (serial, temperature) => {
    try {
      await axios.post(`${API_URL}/api/console/device/${serial}/current-temp`, {
        temperature: temperature
      });
      setSuccess(`Updated current temperature for ${serial} to ${temperature}°F`);
      setCurrentTempDialog({ open: false, device: null, value: 72 });
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update current temperature');
    }
  };

  /* ------------------ Helpers ------------------ */
  const formatTemperature = (temp) => {
    return temp ? `${temp.toFixed(1)}°F` : 'N/A';
  };

  const formatPower = (power) => {
    return power ? `${power.toFixed(3)} kW` : '0.000 kW';
  };

  const getStatusColor = (device) => {
    if (!device.current_state) return 'default';
    if (device.current_state.is_running) return 'success';
    return 'warning';
  };

  const getStatusText = (device) => {
    if (!device.current_state) return 'Unknown';
    if (device.current_state.is_running) return 'Running';
    return 'Idle';
  };

  /* ------------------ Render ------------------ */
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" component="h1">
          🏠 Virtual Thermostat Testbed Console
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadData}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </Box>

      {/* Tabs */}
      <Tabs
        value={tabIndex}
        onChange={(e, idx) => setTabIndex(idx)}
        textColor="primary"
        indicatorColor="primary"
        sx={{ mb: 3 }}
      >
        <Tab icon={<Thermostat />} label="Devices" />
        <Tab icon={<People />} label="Users" />
      </Tabs>

      {refreshing && <LinearProgress sx={{ mb: 2 }} />}

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* ------------------ DEVICES TAB ------------------ */}
      {tabIndex === 0 && (
        <>
          {/* Dashboard Overview */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Active Devices
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.active_devices || devices.length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Power
                  </Typography>
                  <Typography variant="h4">
                    {formatPower(dashboardData?.total_energy_consumption || powerData?.total_power_kw)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Temperature
                  </Typography>
                  <Typography variant="h4">
                    {formatTemperature(dashboardData?.average_temperature)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Homes
                  </Typography>
                  <Typography variant="h4">
                    {powerData?.total_homes || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            {/* Device Spawning */}
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>
                  <Cloud sx={{ mr: 1, verticalAlign: 'bottom' }} />
                  Create New Device
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  Select a home configuration to create a new virtual thermostat
                </Typography>
                <TextField
                  label="Assign to Username"
                  value={usernameInput}
                  onChange={(e) => setUsernameInput(e.target.value)}
                  fullWidth
                  sx={{ mb: 2 }}
                />
                <Box sx={{ mt: 1 }}>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    onClick={() => spawnDevice('small_apartment_efficient.yaml')}
                    disabled={loading}
                    sx={{ mb: 1 }}
                    startIcon={<Thermostat />}
                  >
                    🏢 Small Apartment (Efficient)
                  </Button>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    onClick={() => spawnDevice('small_apartment_inefficient.yaml')}
                    disabled={loading}
                    sx={{ mb: 1 }}
                    startIcon={<Thermostat />}
                  >
                    🏢 Small Apartment (Inefficient)
                  </Button>
                  <Button 
                    variant="contained" 
                    fullWidth 
                    onClick={() => spawnDevice('medium_house_efficient.yaml')}
                    disabled={loading}
                    startIcon={<Thermostat />}
                  >
                    🏠 Medium House (Efficient)
                  </Button>
                </Box>
                {loading && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <CircularProgress />
                    <Typography sx={{ ml: 2 }}>Creating device...</Typography>
                  </Box>
                )}
              </Paper>
            </Grid>

            {/* Device List */}
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>
                  <Thermostat sx={{ mr: 1, verticalAlign: 'bottom' }} />
                  Active Devices ({devices.length})
                </Typography>
                
                {devices.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h6" color="textSecondary">
                      No devices found
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Create your first virtual thermostat using the panel on the left
                    </Typography>
                  </Box>
                ) : (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Device ID</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Current Temp</TableCell>
                          <TableCell>Target Temp</TableCell>
                          <TableCell>Mode</TableCell>
                          <TableCell>Power</TableCell>
                          <TableCell>Config</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {devices.map((device) => (
                          <TableRow key={device.serial_number}>
                            <TableCell>
                              <Typography variant="body2" fontWeight="bold">
                                {device.serial_number}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                Created: {device.created_at ? new Date(device.created_at).toLocaleDateString() : 'Unknown'}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={getStatusText(device)}
                                color={getStatusColor(device)}
                                size="small"
                                icon={device.current_state?.is_running ? <PlayArrow /> : <Stop />}
                              />
                            </TableCell>
                            <TableCell>
                              {formatTemperature(device.current_state?.temperature)}
                            </TableCell>
                            <TableCell>
                              {formatTemperature(device.current_state?.target_temp)}
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={device.current_state?.mode || 'Unknown'}
                                variant="outlined"
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              {formatPower(device.current_state?.power_kw)}
                            </TableCell>
                            <TableCell>
                              <Typography variant="caption">
                                {device.config_file || 'Unknown'}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Stack direction="row" spacing={1}>
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => setControlDialog({ open: true, device })}
                                  title="Control device"
                                >
                                  <Settings />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => setDeleteDialog({ open: true, device })}
                                  title="Delete device"
                                >
                                  <Delete />
                                </IconButton>
                              </Stack>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </Paper>
            </Grid>

            {/* Power Consumption Details */}
            {powerData && powerData.homes && powerData.homes.length > 0 && (
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h5" gutterBottom>
                    <TrendingUp sx={{ mr: 1, verticalAlign: 'bottom' }} />
                    Real-time Power Consumption
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Home ID</TableCell>
                          <TableCell>Power (kW)</TableCell>
                          <TableCell>HVAC State</TableCell>
                          <TableCell>Indoor Temp</TableCell>
                          <TableCell>Outdoor Temp</TableCell>
                          <TableCell>Setpoint</TableCell>
                          <TableCell>Home Size</TableCell>
                          <TableCell>Configuration</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {powerData.homes.map((home) => (
                          <TableRow key={home.home_id}>
                            <TableCell fontWeight="bold">{home.home_id}</TableCell>
                            <TableCell>
                              <Typography color={home.power_kw > 1 ? 'error.main' : 'text.primary'}>
                                {formatPower(home.power_kw)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={home.hvac_state}
                                color={home.hvac_state === 'off' ? 'default' : 'primary'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>{formatTemperature(home.indoor_temp)}</TableCell>
                            <TableCell>{formatTemperature(home.outdoor_temp)}</TableCell>
                            <TableCell>{formatTemperature(home.setpoint)}</TableCell>
                            <TableCell>{home.home_size_sqft} sq ft</TableCell>
                            <TableCell>
                              <Typography variant="caption">
                                {home.config_name}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>
            )}
          </Grid>
        </>
      )}

      {/* ------------------ USERS TAB ------------------ */}
      {tabIndex === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                <People sx={{ mr: 1, verticalAlign: 'bottom' }} />
                User Management ({users.length})
              </Typography>
              {users.length === 0 ? (
                <Typography>No users found.</Typography>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>ID</TableCell>
                        <TableCell>Username</TableCell>
                        <TableCell>Created</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {users.map((u) => (
                        <TableRow key={u.id}>
                          <TableCell>{u.id}</TableCell>
                          <TableCell>{u.username}</TableCell>
                          <TableCell>{u.created_at ? new Date(u.created_at).toLocaleString() : 'N/A'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                Add New User
              </Typography>
              <TextField
                label="Username"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <TextField
                label="Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                onClick={createUser}
                disabled={userLoading}
              >
                {userLoading ? 'Creating...' : 'Create User'}
              </Button>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* ------------ Device Dialogs (unchanged) ------------ */}
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, device: null })}
      >
        <DialogTitle>Delete Device</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete device "{deleteDialog.device?.serial_number}"?
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            This action cannot be undone. The device containers will be stopped and removed.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, device: null })}>
            Cancel
          </Button>
          <Button 
            onClick={() => deleteDevice(deleteDialog.device?.serial_number)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Control Device Dialog */}
      <Dialog
        open={controlDialog.open}
        onClose={() => setControlDialog({ open: false, device: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Control Device: {controlDialog.device?.serial_number}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<DeviceThermostat />}
                  onClick={() => {
                    setSetpointDialog({ 
                      open: true, 
                      device: controlDialog.device, 
                      value: controlDialog.device?.current_state?.target_temp || 72 
                    });
                    setControlDialog({ open: false, device: null });
                  }}
                >
                  Adjust Temperature Setpoint
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<AcUnit />}
                  onClick={() => {
                    setModeDialog({ 
                      open: true, 
                      device: controlDialog.device, 
                      value: controlDialog.device?.current_state?.mode || 'auto' 
                    });
                    setControlDialog({ open: false, device: null });
                  }}
                >
                  Change Operating Mode
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<WbSunny />}
                  onClick={() => {
                    setWeatherDialog({ 
                      open: true, 
                      device: controlDialog.device, 
                      value: 85 
                    });
                    setControlDialog({ open: false, device: null });
                  }}
                >
                  Override Outdoor Temperature
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Thermostat />}
                  onClick={() => {
                    setCurrentTempDialog({ 
                      open: true, 
                      device: controlDialog.device, 
                      value: controlDialog.device?.current_state?.temperature || 72 
                    });
                    setControlDialog({ open: false, device: null });
                  }}
                >
                  Adjust Current Indoor Temperature
                </Button>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setControlDialog({ open: false, device: null })}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Temperature Setpoint Dialog */}
      <Dialog
        open={setpointDialog.open}
        onClose={() => setSetpointDialog({ open: false, device: null, value: 72 })}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>
          Set Temperature: {setpointDialog.device?.serial_number}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, pb: 1 }}>
            <Typography gutterBottom>
              Target Temperature: {setpointDialog.value}°F
            </Typography>
            <Slider
              value={setpointDialog.value}
              onChange={(e, value) => setSetpointDialog({ ...setpointDialog, value })}
              min={60}
              max={90}
              step={1}
              marks
              valueLabelDisplay="on"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSetpointDialog({ open: false, device: null, value: 72 })}>
            Cancel
          </Button>
          <Button 
            onClick={() => updateSetpoint(setpointDialog.device?.serial_number, setpointDialog.value)}
            variant="contained"
          >
            Apply
          </Button>
        </DialogActions>
      </Dialog>

      {/* Mode Selection Dialog */}
      <Dialog
        open={modeDialog.open}
        onClose={() => setModeDialog({ open: false, device: null, value: 'auto' })}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>
          Set Mode: {modeDialog.device?.serial_number}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Operating Mode</InputLabel>
              <Select
                value={modeDialog.value}
                onChange={(e) => setModeDialog({ ...modeDialog, value: e.target.value })}
                label="Operating Mode"
              >
                <MenuItem value="off">Off</MenuItem>
                <MenuItem value="heat">Heat</MenuItem>
                <MenuItem value="cool">Cool</MenuItem>
                <MenuItem value="auto">Auto</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModeDialog({ open: false, device: null, value: 'auto' })}>
            Cancel
          </Button>
          <Button 
            onClick={() => updateMode(modeDialog.device?.serial_number, modeDialog.value)}
            variant="contained"
          >
            Apply
          </Button>
        </DialogActions>
      </Dialog>

      {/* Weather Override Dialog */}
      <Dialog
        open={weatherDialog.open}
        onClose={() => setWeatherDialog({ open: false, device: null, value: 85 })}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>
          Override Outdoor Temperature: {weatherDialog.device?.serial_number}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, pb: 1 }}>
            <Typography gutterBottom>
              Outdoor Temperature: {weatherDialog.value}°F
            </Typography>
            <Slider
              value={weatherDialog.value}
              onChange={(e, value) => setWeatherDialog({ ...weatherDialog, value })}
              min={0}
              max={120}
              step={1}
              marks
              valueLabelDisplay="on"
              color="warning"
            />
            <Typography variant="caption" color="textSecondary">
              This will override the simulated outdoor temperature for this device for the next hour.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWeatherDialog({ open: false, device: null, value: 85 })}>
            Cancel
          </Button>
          <Button 
            onClick={() => overrideWeather(weatherDialog.device?.serial_number, weatherDialog.value)}
            variant="contained"
            color="warning"
          >
            Apply Override
          </Button>
        </DialogActions>
      </Dialog>

      {/* Current Temperature Adjustment Dialog */}
      <Dialog
        open={currentTempDialog.open}
        onClose={() => setCurrentTempDialog({ open: false, device: null, value: 72 })}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>
          Adjust Current Indoor Temperature: {currentTempDialog.device?.serial_number}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, pb: 1 }}>
            <Typography gutterBottom>
              Current Indoor Temperature: {currentTempDialog.value}°F
            </Typography>
            <Slider
              value={currentTempDialog.value}
              onChange={(e, value) => setCurrentTempDialog({ ...currentTempDialog, value })}
              min={50}
              max={100}
              step={0.5}
              marks
              valueLabelDisplay="on"
              color="secondary"
            />
            <Typography variant="caption" color="textSecondary">
              This will immediately adjust the current indoor temperature for testing purposes.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCurrentTempDialog({ open: false, device: null, value: 72 })}>
            Cancel
          </Button>
          <Button 
            onClick={() => updateCurrentTemp(currentTempDialog.device?.serial_number, currentTempDialog.value)}
            variant="contained"
            color="secondary"
          >
            Apply
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default App;
