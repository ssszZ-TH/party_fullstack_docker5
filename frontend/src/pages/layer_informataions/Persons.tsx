import React, { useState, useEffect, useContext } from 'react';
import { Box, Container, Typography, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { getPersons } from '../../services/persons';
import { useTheme } from '../../contexts/ThemeContext';
import { AuthContext } from '../../contexts/AuthContext';
import DataTable from '../../components/DataTable';
import AppBarCustom from '../../components/AppBarCustom';
import UpdateButton from '../../components/buttons/UpdateButton';
import AddButton from '../../components/buttons/AddButton';
import Loading from '../../components/Loading';
import { GridColDef } from '@mui/x-data-grid';
import { formatDateTime } from '../../utils/time_util';

interface Person {
  id: number;
  username: string;
  email: string;
  personal_id_number: string;
  first_name: string;
  middle_name: string | null;
  last_name: string;
  nick_name: string | null;
  birth_date: string;
  gender_type_id: number | null;
  marital_status_type_id: number | null;
  country_id: number | null;
  height: number;
  weight: number;
  racial_type_id: number | null;
  income_range_id: number | null;
  about_me: string | null;
  created_at: string;
  updated_at: string | null;
}

export default function Persons() {
  const { isDarkMode } = useTheme();
  const { logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [persons, setPersons] = useState<Person[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPersons = async () => {
      setLoading(true);
      try {
        const token = Cookies.get('access_token');
        if (!token) {
          setError('กรุณาเข้าสู่ระบบหรือ token หมดอายุ');
          logout();
          navigate('/login');
          return;
        }
        const data = await getPersons();
        if (Array.isArray(data)) {
          setPersons(data.filter(person => person && typeof person === 'object' && 'id' in person));
          setError(null);
        } else {
          setError('Invalid data format received');
        }
      } catch (err: any) {
        if (err.message === 'No access token found' || err.response?.status === 401) {
          setError('กรุณาเข้าสู่ระบบหรือ token หมดอายุ');
          logout();
          navigate('/login');
        } else {
          setError(err.message || 'ไม่สามารถโหลดข้อมูลได้');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchPersons();
  }, [navigate, logout]);

  const columns: GridColDef[] = [
    {
      field: 'actions',
      headerName: 'Actions',
      width: 100,
      renderCell: (params) => (
        params.id ? (
          <UpdateButton
            onClick={() => navigate(`/persons/${params.id}`)}
          />
        ) : null
      ),
    },
    { field: 'id', headerName: 'ID', width: 90 },
    { field: 'username', headerName: 'Username', width: 150 },
    { field: 'email', headerName: 'Email', width: 200 },
    { field: 'personal_id_number', headerName: 'Personal ID', width: 150 },
    { field: 'first_name', headerName: 'First Name', width: 150 },
    { field: 'middle_name', headerName: 'Middle Name', width: 150, valueFormatter: (value: string | null) => value || 'N/A' },
    { field: 'last_name', headerName: 'Last Name', width: 150 },
    { field: 'nick_name', headerName: 'Nick Name', width: 150, valueFormatter: (value: string | null) => value || 'N/A' },
    {
      field: 'birth_date',
      headerName: 'Birth Date',
      width: 150,
      valueFormatter: (value: string | null) => value ? new Date(value).toLocaleDateString('th-TH', { timeZone: 'Asia/Bangkok' }) : 'N/A',
    },
    { field: 'gender_type_id', headerName: 'Gender Type ID', width: 120, valueFormatter: (value: number | null) => value ?? 'N/A' },
    { field: 'marital_status_type_id', headerName: 'Marital Status ID', width: 120, valueFormatter: (value: number | null) => value ?? 'N/A' },
    { field: 'country_id', headerName: 'Country ID', width: 100, valueFormatter: (value: number | null) => value ?? 'N/A' },
    { field: 'height', headerName: 'Height (cm)', width: 100 },
    { field: 'weight', headerName: 'Weight (kg)', width: 100 },
    { field: 'racial_type_id', headerName: 'Racial Type ID', width: 120, valueFormatter: (value: number | null) => value ?? 'N/A' },
    { field: 'income_range_id', headerName: 'Income Range ID', width: 120, valueFormatter: (value: number | null) => value ?? 'N/A' },
    { field: 'about_me', headerName: 'About Me', width: 200, valueFormatter: (value: string | null) => value || 'N/A' },
    {
      field: 'created_at',
      headerName: 'Created At',
      width: 180,
      valueFormatter: (value: string | null) => formatDateTime(value),
    },
    {
      field: 'updated_at',
      headerName: 'Updated At',
      width: 180,
      valueFormatter: (value: string | null) => formatDateTime(value),
    },
  ];

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', display: 'flex', flexDirection: 'column' }}>
      <AppBarCustom title="Persons" />
      <Container maxWidth="lg" sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" sx={{ color: 'text.primary' }}>
            All Persons
          </Typography>
          <AddButton onClick={() => navigate('/persons/create')} />
        </Box>
        {loading ? (
          <Loading />
        ) : error ? (
          <Alert severity="error" sx={{ m: 2 }}>
            {error}
          </Alert>
        ) : (
          <Box sx={{ height: 'calc(100vh - 200px)', width: '100%' }}>
            <DataTable
              columns={columns}
              rows={persons}
              getRowId={(row) => row.id}
            />
          </Box>
        )}
      </Container>
    </Box>
  );
}