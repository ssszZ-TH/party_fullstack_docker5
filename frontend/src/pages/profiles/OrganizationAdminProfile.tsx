import React, { useState, useEffect } from "react";
import { Box, Container, Typography, Paper, Stack, Button } from "@mui/material";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";
import { getMyProfile } from "../../services/auth";
import { useTheme } from "../../contexts/ThemeContext";
import { AuthContext } from "../../contexts/AuthContext";
import AppBarCustom from "../../components/AppBarCustom";

interface UserProfile {
  id: number;
  username: string;
  email: string;
  role: string;
  created_at: string;
  updated_at: string | null;
}

export default function OrganizationAdminProfile() {
  const { isDarkMode } = useTheme();
  const { setIsAuthenticated } = React.useContext(AuthContext);
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = Cookies.get("access_token");
        if (!token) {
          navigate("/login");
          return;
        }
        const data = await getMyProfile(token);
        setProfile(data);
      } catch (error) {
        console.error("Error fetching profile:", error);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [navigate]);

  const handleHome = () => {
    navigate("/homes/organization-admin");
  };

  const handleLogout = () => {
    Cookies.remove("access_token");
    Cookies.remove("role");
    setIsAuthenticated(false);
    navigate("/login");
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!profile) {
    return <div>No profile data available</div>;
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('th-TH', {
      timeZone: 'Asia/Bangkok',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBarCustom title="Organization Admin Profile" />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4, borderRadius: "shape.borderRadius", bgcolor: "background.paper" }}>
          <Typography variant="h4" sx={{ color: "text.primary", mb: 2 }}>
            Profile
          </Typography>
          <Box sx={{ mb: 4 }}>
            <Typography variant="body1" sx={{ color: "text.primary" }}>
              <strong>ID:</strong> {profile.id}
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary" }}>
              <strong>Username:</strong> {profile.username}
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary" }}>
              <strong>Email:</strong> {profile.email}
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary" }}>
              <strong>Role:</strong> {profile.role}
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary" }}>
              <strong>Created At:</strong> {formatDateTime(profile.created_at)}
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary" }}>
              <strong>Updated At:</strong> {profile.updated_at ? formatDateTime(profile.updated_at) : "N/A"}
            </Typography>
          </Box>
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button
              variant="contained"
              onClick={handleHome}
              sx={{
                backgroundColor: "primary.main",
                color: "primary.contrastText",
                "&:hover": { backgroundColor: "primary.dark" },
                textTransform: "none",
                borderRadius: "shape.borderRadius",
              }}
            >
              Home
            </Button>
            <Button
              variant="contained"
              onClick={handleLogout}
              sx={{
                backgroundColor: "error.main",
                color: "error.contrastText",
                "&:hover": { backgroundColor: "error.dark" },
                textTransform: "none",
                borderRadius: "shape.borderRadius",
              }}
            >
              Logout
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}