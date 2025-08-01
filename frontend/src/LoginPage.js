// src/LoginPage.js
import React, { useState, useEffect } from "react";
import {
  TextField,
  Button,
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
} from "@mui/material";
import axios from "axios";

const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [usuario, setUsuario] = useState(null);
  const [devices, setDevices] = useState([]);

  const handleLogin = async () => {
    try {
      const res = await axios.get("http://localhost:8000/usuarios/");
      const users = res.data;
      const user = users.find((u) => u.correo === email);
      if (user) {
        setUsuario(user);
        const dres = await axios.get("http://localhost:8000/devices/");
        const userDevices = dres.data.filter((d) => d.usuario_id === user.id);
        setDevices(userDevices);
      } else {
        alert("Usuario no encontrado");
      }
    } catch (err) {
      console.error("Error al obtener datos:", err);
    }
  };

  return (
    <Container>
      {!usuario ? (
        <Box sx={{ mt: 8 }}>
          <Typography variant="h4" gutterBottom>Ingresar</Typography>
          <TextField
            label="Correo"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />
          <Button variant="contained" onClick={handleLogin}>Entrar</Button>
        </Box>
      ) : (
        <Box sx={{ mt: 8 }}>
          <Typography variant="h5">Dispositivos de {usuario.nombre}</Typography>
          <Grid container spacing={2} sx={{ mt: 2 }}>
            {devices.map((device) => (
              <Grid item xs={12} sm={6} md={4} key={device.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">{device.nombre}</Typography>
                    <Typography variant="body2">Tipo: {device.tipo}</Typography>
                    <Typography variant="body2">Firmware: {device.firmware_version}</Typography>
                    <Typography variant="body2">Estado: {device.estado}</Typography>
                    <Typography variant="body2">Asignado: {device.asignado_a_producto ? "Sí" : "No"}</Typography>
                    <Typography variant="body2">Producto ID: {device.producto_id}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  );
};

export default LoginPage;
