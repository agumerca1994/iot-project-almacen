import React, { useEffect, useRef, useState } from "react";
import MoreVertIcon from '@mui/icons-material/MoreVert';
import Menu from '@mui/material/Menu';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  TextField,
  Card,
  CardContent,
  Grid,
  Modal,
  Box,
  IconButton,
  MenuItem,
  Select,
  InputLabel,
  FormControl
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import axios from "axios";

const modalStyle = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "90%",
  maxWidth: 400,
  bgcolor: "background.paper",
  boxShadow: 24,
  p: 4,
  display: "flex",
  flexDirection: "column",
  gap: 2
};

function App() {
  // --- Menú de acciones para dispositivos ---
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [openEditModal, setOpenEditModal] = useState(false);
  const [editTipo, setEditTipo] = useState("");
  const [editProducto, setEditProducto] = useState("");

  const handleMenuOpen = (event, device) => {
    setAnchorEl(event.currentTarget);
    setSelectedDevice(device);
  };
  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedDevice(null);
  };

  // --- EDITAR ---
  const handleEdit = () => {
    setEditTipo(selectedDevice?.tipo || "");
    setEditProducto(selectedDevice?.producto_id || "");
    setOpenEditModal(true);
    handleMenuClose();
  };
  const handleEditSave = async () => {
    if (!selectedDevice) return;
    if (window.confirm("¿Confirmas los cambios?")) {
      await axios.put(`http://localhost:8000/devices/${selectedDevice.id}`, {
        producto_id: editProducto,
        tipo: editTipo
      });
      fetchDevices(userId);
      setOpenEditModal(false);
    }
  };

  // --- DESASIGNAR ---
  const handleUnassign = async () => {
    handleMenuClose();
    if (!selectedDevice) return;
    if (window.confirm("¿Seguro que quieres desasignar este dispositivo?")) {
      await axios.put(`http://localhost:8000/devices/${selectedDevice.id}/unassign`);
      fetchDevices(userId);
    }
  };

  // --- ELIMINAR ---
  const handleDelete = async () => {
    handleMenuClose();
    if (!selectedDevice) return;
    if (window.confirm("Al eliminar el dispositivo se perderán todos los datos. ¿Continuar?")) {
      await axios.delete(`http://localhost:8000/devices/${selectedDevice.id}`);
      fetchDevices(userId);
    }
  };

  // --- COMANDOS ---
  const handleCommand = async (cmd) => {
    handleMenuClose();
    if (!selectedDevice) return;
    let msg = "";
    if (cmd === "reset") msg = "¿Seguro que quieres resetear el dispositivo?";
    if (cmd === "reset_all") msg = "¿Seguro que quieres restablecer el dispositivo? Se perderán configuraciones y asignación.";
    if (window.confirm(msg)) {
      await axios.post(`http://localhost:8000/devices/${selectedDevice.id}/command`, { command: cmd });
    }
  };
  const [email, setEmail] = useState("");
  const [userId, setUserId] = useState(() => localStorage.getItem("userId"));
  const [userCorreo, setUserCorreo] = useState(() => localStorage.getItem("correo"));
  const [devices, setDevices] = useState([]);
  const [productos, setProductos] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [openNuevoProducto, setOpenNuevoProducto] = useState(false);
  const [nuevoProductoNombre, setNuevoProductoNombre] = useState("");
  const [nuevoProductoVencimiento, setNuevoProductoVencimiento] = useState("");
  const [productoSeleccionado, setProductoSeleccionado] = useState("");
  const [nuevoDispositivo, setNuevoDispositivo] = useState({
    serial_number: "",
    clave: "",
    tipo: "balanza",
    comentarios: ""
  });
  const [errorDispositivo, setErrorDispositivo] = useState("");

  const ws = useRef(null);

  const fetchDevices = async (id) => {
    try {
      const [resDevices, resAlacena] = await Promise.all([
        axios.get("http://localhost:8000/devices/"),
        axios.get("http://localhost:8000/alacena/")
      ]);

      const userDevices = resDevices.data.filter(d => d.usuario_id === Number(id));

      const enrichedDevices = userDevices.map(device => {
        const alacenaItem = resAlacena.data.find(a => a.product_id === device.producto_id);
        return {
          ...device,
          cantidad: alacenaItem ? alacenaItem.quantity : 0
        };
      });

      setDevices(enrichedDevices);
    } catch (error) {
      console.error("Error al obtener dispositivos o alacena", error);
    }
  };

  const fetchProductos = async () => {
    try {
      const res = await axios.get("http://localhost:8000/productos/");
      setProductos(res.data);
    } catch (error) {
      console.error("Error al obtener productos", error);
    }
  };

  const handleLogin = async () => {
    try {
      const res = await axios.get("http://localhost:8000/usuarios/");
      const user = res.data.find(u => u.correo === email);

      if (user) {
        setUserId(user.id);
        setUserCorreo(user.correo);
        localStorage.setItem("userId", user.id);
        localStorage.setItem("correo", user.correo);
        fetchDevices(user.id);
        fetchProductos();
      } else {
        alert("Usuario no encontrado");
      }
    } catch (error) {
      alert("Error al conectarse con la API");
    }
  };

  const handleLogout = () => {
    setUserId(null);
    setUserCorreo(null);
    setDevices([]);
    localStorage.removeItem("userId");
    localStorage.removeItem("correo");
    if (ws.current) ws.current.close();
  };

  const handleGuardarProducto = async () => {
    try {
      const nuevo = {
        nombre: nuevoProductoNombre,
        usuario_id: Number(userId)
      };
      await axios.post("http://localhost:8000/productos/", nuevo);
      setOpenNuevoProducto(false);
      setNuevoProductoNombre("");
      setNuevoProductoVencimiento("");
      fetchProductos();
    } catch (err) {
      alert("Error al guardar producto");
      console.error(err);
    }
  };

  const handleGuardarDispositivo = async () => {
    setErrorDispositivo("");
    try {
      // Validar primero con el backend
      const serial = nuevoDispositivo.serial_number.trim();
      const clave = nuevoDispositivo.clave.trim();
      if (!serial || !clave) {
        setErrorDispositivo("Debes ingresar número de serie y clave");
        return;
      }
      const resp = await axios.get(`http://localhost:8000/global-devices/serial/${serial}`);
      const globalDevice = resp.data;
      if (!globalDevice) {
        setErrorDispositivo("No se encontró el dispositivo global");
        return;
      }
      if (globalDevice.estado !== "libre") {
        setErrorDispositivo("No se puede asignar, el dispositivo ya tiene un producto y usuario asignado");
        return;
      }
      if (globalDevice.password !== clave) {
        setErrorDispositivo("La clave del producto no coincide");
        return;
      }
      // Si todo OK, guardar
      const payload = {
        serial_number: serial,
        nombre: "string",
        estado: "asignado",
        tipo: nuevoDispositivo.tipo,
        firmware_version: "fm010",
        asignado_a_producto: true,
        comentarios: nuevoDispositivo.comentarios,
        producto_id: Number(productoSeleccionado),
        usuario_id: Number(userId)
      };
      await axios.post("http://localhost:8000/devices/", payload);
      setOpenModal(false);
      setNuevoDispositivo({ serial_number: "", clave: "", tipo: "balanza", comentarios: "" });
    } catch (error) {
      setErrorDispositivo("Error al guardar dispositivo o validar datos");
      console.error(error);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchDevices(userId);
      fetchProductos();

      ws.current = new WebSocket("ws://localhost:8000/ws/devices");

      ws.current.onopen = () => console.log("✅ WebSocket conectado");
      ws.current.onerror = (err) => console.error("❌ WebSocket error:", err);

      ws.current.onmessage = async (event) => {
        const message = JSON.parse(event.data);

        if (message.type === "device") {
          const newDevice = message.data;
          if (newDevice.usuario_id === Number(userId)) {
            try {
              const resAlacena = await axios.get("http://localhost:8000/alacena/");
              const alacenaItem = resAlacena.data.find(a => a.product_id === newDevice.producto_id);
              const cantidad = alacenaItem ? alacenaItem.quantity : 0;

              setDevices(prev => [...prev, { ...newDevice, cantidad }]);
            } catch (err) {
              console.error("Error al actualizar cantidad para nuevo dispositivo", err);
            }
          }
        }

        if (message.type === "stock") {
          const { product_id, quantity } = message.data;
          setDevices(prev => prev.map(device =>
            device.producto_id === product_id
              ? { ...device, cantidad: quantity }
              : device
          ));
        }
      };

      return () => {
        if (ws.current) {
          ws.current.close();
          console.log("🛑 WebSocket cerrado");
        }
      };
    }
  }, [userId]);

  return (
    <>
      {userId && (
        <AppBar position="static" sx={{ mb: 4 }}>
          <Toolbar sx={{ justifyContent: "space-between" }}>
            <Typography variant="h6">Alacena IoT</Typography>
            <Button color="inherit" onClick={handleLogout}>Cerrar sesión</Button>
          </Toolbar>
        </AppBar>
      )}

      <Container sx={{ mt: 4 }}>
        {!userId ? (
          <>
            <Typography variant="h5" sx={{ mb: 2 }}>Ingresar con email</Typography>
            <TextField label="Email" value={email} onChange={e => setEmail(e.target.value)} fullWidth />
            <Button variant="contained" onClick={handleLogin} sx={{ mt: 2 }}>Ingresar</Button>
          </>
        ) : (
          <>
            <Typography variant="h5" sx={{ mb: 2 }}>Mis Dispositivos</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={4}>
                <Card
                  sx={{ backgroundColor: "#e0f7fa", borderRadius: 2, boxShadow: 3, cursor: "pointer", height: "100%" }}
                  onClick={() => setOpenModal(true)}
                >
                  <CardContent sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <AddIcon fontSize="large" />
                    <Typography variant="h6">Agregar dispositivo</Typography>
                  </CardContent>
                </Card>
              </Grid>
              {devices.map(device => (
                <Grid item xs={12} sm={6} md={4} key={device.id}>
                  <Card sx={{ backgroundColor: "#f5f5f5", borderRadius: 2, boxShadow: 3 }}>
                    <CardContent sx={{ position: 'relative' }}>
                      <Typography variant="h6">{device.nombre}</Typography>
                      <Typography variant="body1">Cantidad: {device.cantidad}</Typography>
                      <IconButton
                        aria-label="acciones"
                        onClick={e => handleMenuOpen(e, device)}
                        sx={{ position: 'absolute', top: 8, right: 8 }}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
      
      {/* Menú de acciones */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleEdit}>Editar</MenuItem>
        <MenuItem onClick={handleUnassign}>Desasignar</MenuItem>
        <MenuItem onClick={handleDelete}>Eliminar</MenuItem>
        <MenuItem onClick={() => handleCommand("reset")}>Comando: Resetear</MenuItem>
        <MenuItem onClick={() => handleCommand("reset_all")}>Comando: Restablecer</MenuItem>
      </Menu>

      {/* Modal de edición */}
      <Modal open={openEditModal} onClose={() => setOpenEditModal(false)}>
        <Box sx={modalStyle}>
          <Typography variant="h6" gutterBottom>Editar dispositivo</Typography>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="edit-producto-label">Producto</InputLabel>
            <Select
              labelId="edit-producto-label"
              value={editProducto}
              label="Producto"
              onChange={e => setEditProducto(e.target.value)}
            >
              {productos.map((prod) => (
                <MenuItem key={prod.id} value={prod.id}>{prod.nombre}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="edit-tipo-label">Tipo de medición por</InputLabel>
            <Select
              labelId="edit-tipo-label"
              value={editTipo}
              label="Tipo de medición por"
              onChange={e => setEditTipo(e.target.value)}
            >
              <MenuItem value="peso">Peso</MenuItem>
              <MenuItem value="cantidad">Cantidad</MenuItem>
            </Select>
          </FormControl>
          <Box sx={{ display: "flex", justifyContent: "space-between" }}>
            <Button variant="outlined" onClick={() => setOpenEditModal(false)}>Cancelar</Button>
            <Button variant="contained" onClick={handleEditSave}>Guardar</Button>
          </Box>
        </Box>
      </Modal>
            </Grid>
          </>
        )}
      </Container>

      <Modal open={openModal} onClose={() => setOpenModal(false)}>
        <Box sx={modalStyle}>
          <Typography variant="h6" gutterBottom>Agregar nuevo dispositivo</Typography>
          {errorDispositivo && (
            <Typography color="error" sx={{ mb: 2 }}>{errorDispositivo}</Typography>
          )}
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FormControl fullWidth>
                <InputLabel id="producto-label">Producto</InputLabel>
                <Select
                  labelId="producto-label"
                  value={productoSeleccionado}
                  label="Producto"
                  onChange={e => setProductoSeleccionado(e.target.value)}
                  disabled={productos.length === 0}
                >
                  {productos.length === 0 ? (
                    <MenuItem value="" disabled>Aun no tenes productos creados</MenuItem>
                  ) : (
                    productos.map((prod) => (
                      <MenuItem key={prod.id} value={prod.id}>{prod.nombre}</MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
              <Button variant="outlined" onClick={() => setOpenNuevoProducto(true)} sx={{ whiteSpace: 'nowrap', minWidth: 80 }}>crear</Button>
            </Box>
            <TextField label="Número de serie" fullWidth value={nuevoDispositivo.serial_number} onChange={e => setNuevoDispositivo({ ...nuevoDispositivo, serial_number: e.target.value })} />
            <TextField label="Clave de producto" type="password" fullWidth value={nuevoDispositivo.clave} onChange={e => setNuevoDispositivo({ ...nuevoDispositivo, clave: e.target.value })} />
            <FormControl fullWidth>
              <InputLabel id="tipo-label">Tipo de medición por</InputLabel>
              <Select
                labelId="tipo-label"
                value={nuevoDispositivo.tipo}
                onChange={e => setNuevoDispositivo({ ...nuevoDispositivo, tipo: e.target.value })}
                label="Tipo de medición por"
              >
                <MenuItem value="peso">Peso</MenuItem>
                <MenuItem value="cantidad">Cantidad</MenuItem>
              </Select>
            </FormControl>
            <TextField label="Comentarios" fullWidth value={nuevoDispositivo.comentarios} onChange={e => setNuevoDispositivo({ ...nuevoDispositivo, comentarios: e.target.value })} />
          </Box>
          <Box sx={{ mt: 3, display: "flex", justifyContent: "space-between" }}>
            <Button variant="outlined" onClick={() => setOpenModal(false)}>Cancelar</Button>
            <Button variant="contained" onClick={handleGuardarDispositivo}>Guardar</Button>
          </Box>
        </Box>
      </Modal>

      <Modal open={openNuevoProducto} onClose={() => setOpenNuevoProducto(false)}>
        <Box sx={modalStyle}>
          <Typography variant="h6" gutterBottom>Nuevo Producto</Typography>
          <TextField label="Nombre del producto" value={nuevoProductoNombre} onChange={e => setNuevoProductoNombre(e.target.value)} fullWidth />
          <TextField label="Fecha de vencimiento" type="date" InputLabelProps={{ shrink: true }} fullWidth value={nuevoProductoVencimiento} onChange={e => setNuevoProductoVencimiento(e.target.value)} />
          <Box sx={{ display: "flex", justifyContent: "space-between", mt: 2 }}>
            <Button variant="outlined" onClick={() => setOpenNuevoProducto(false)}>Cancelar</Button>
            <Button variant="contained" onClick={handleGuardarProducto}>Guardar</Button>
          </Box>
        </Box>
      </Modal>
    </>
  );
}

export default App;
